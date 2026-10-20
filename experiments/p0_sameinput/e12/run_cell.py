"""2x2 factorial cell runner (PREREG_e12.md). d1 prompt = fixed system + rendered state + one branch per question,
so a cell is exactly (state, questions). Reuses pairwise.select_input / compact_signal and infer.load; no new harness.
  state:     compact = pairwise select state (compact_signal + compact_work)   | full = case view as infer.py passes it
  questions: select  = pairwise select question (PARA variant 0) -> P(W001)    | formation = case questions -> P(MERGE)+P(UPDATE)
usage: run_cell.py <compact|full> <select|formation> <out.jsonl>   (pair cases of dev_real only)"""
import json, os, sys, time, pathlib
L = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(L/"adapters"))
import infer, pairwise

state_kind, q_kind, out_path = sys.argv[1:4]
Q = {k: v[0] if isinstance(v, list) else v for k, v in json.load(open(L/"experiments/pairwise/PARA.questions.json", encoding="utf-8")).items()}
run = infer.load("d1")
with open(L/"experiments/realgold/dev_real.cases.jsonl", encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out:
    for line in f:
        c = json.loads(line)
        if c["kind"] != "pair":
            continue
        v = c["view"]; owner = v["new_signal"]["thread_already_owned_by_work"]
        sel_state, sel_q = pairwise.select_input(pairwise.compact_signal(v), v["candidate_works"], owner, Q)
        state = sel_state if state_kind == "compact" else v
        qs = {"select": sel_q} if q_kind == "select" else c["questions"]
        t = time.perf_counter(); row = {"case_id": c["case_id"]}
        try:
            r = run(state, qs); u = r.get("usage") or {}
            row.update(probs={k: a.get("probabilities") for k, a in r["answers"].items()}, input_tokens=u.get("input_tokens"),
                       truncated=bool(u.get("truncated")), error=None)
        except Exception as e:  # recorded, never hidden: invalid response
            row.update(probs=None, error=f"{type(e).__name__}: {e}"[:300])
        row["latency_ms"] = (time.perf_counter() - t) * 1000
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps({"cell": [state_kind, q_kind], "d1_lora": os.environ.get("D1_LORA")}))
