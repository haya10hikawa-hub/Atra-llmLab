# PREREG_p0.md scorer: AUC, cluster-bootstrap diffs, TP at FM<=k, argmax, truncation. Aggregate only; dev_real only.
import json, pathlib, random, collections, statistics
L = pathlib.Path(__file__).resolve().parents[2]; B = L/"experiments/realgold"; D = pathlib.Path(__file__).parent
cases = {c["case_id"]: c for c in map(json.loads, (B/"dev_real.cases.jsonl").read_text(encoding="utf-8").splitlines())}
pairs = [k for k, c in cases.items() if c["kind"] == "pair"]; sigs = [k for k, c in cases.items() if c["kind"] != "pair"]
y = {k: cases[k]["label"] == "same" for k in pairs}; ys = {k: cases[k]["label"] == "work" for k in sigs}
rows = lambda p: {r["case_id"]: r for r in map(json.loads, p.read_text(encoding="utf-8").splitlines())}


def full(p):  # infer.py answers (Atra 5-way + target)
    R = rows(p); dp = lambda k: R[k]["answers"]["decision"].get("probabilities") or {}
    tp = lambda k: (R[k]["answers"].get("target_work") or {}).get("probabilities") or {}
    mu = lambda k: dp(k).get("MERGE", 0) + dp(k).get("UPDATE", 0)
    am = lambda k: R[k]["answers"]["decision"]["choice"] in ("MERGE", "UPDATE") and (R[k]["answers"].get("target_work") or {}).get("choice") == "W001"
    return {"s": mu, "s2": lambda k: mu(k) * tp(k).get("W001", 0), "sig": lambda k: 1 - dp(k).get("IGNORE", 0), "am": am,
            "trunc": sum(bool(r.get("truncated")) for r in R.values()), "err": sum(bool(r.get("error")) for r in R.values()),
            "tok": statistics.median(r.get("input_tokens") or 0 for r in R.values())}


def compact(a):  # pairwise.py select probs + argmax answers
    P, A = rows(B/"dev"/a/"probs.jsonl"), rows(B/"dev"/a/"answers.jsonl")
    s = lambda k: list(P[k]["pairs"].values())[0]["same"] if P[k]["pairs"] else 0.0
    am = lambda k: A[k]["answers"]["decision"]["choice"] in ("MERGE", "UPDATE") and (A[k]["answers"].get("target_work") or {}).get("choice") == "W001"
    return {"s": s, "s2": s, "sig": lambda k: P[k]["is_work"], "am": am, "trunc": sum(bool(r.get("truncated")) for r in P.values()),
            "err": sum(bool(r.get("error")) for r in P.values()), "tok": None}


C = {"C1a": compact("base"), "C1b": compact("la10"), "C3": full(B/"dev/jev-latest/answers.jsonl")}
for c in ("C2a", "C2b", "C4"):
    if (D/c/"answers.jsonl").exists(): C[c] = full(D/c/"answers.jsonl")


def auc(ks, s, yy):
    pos = [s(k) for k in ks if yy[k]]; neg = [s(k) for k in ks if not yy[k]]
    return sum((p > n) + .5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def tp_at(s, kfm):
    srt = sorted(pairs, key=s, reverse=True); tp = fp = best = 0
    for i, k in enumerate(srt):
        tp += y[k]; fp += not y[k]
        if fp <= kfm and (i + 1 == len(srt) or s(srt[i + 1]) < s(k)): best = max(best, tp)
    return best


cl = collections.defaultdict(list)
for k in pairs: cl[cases[k]["view"]["new_signal"]["thread_key"]].append(k)
cls = list(cl.values())


def boot(a, b, n=2000):
    rnd = random.Random(0); d = []
    for _ in range(n):
        ks = [k for c in rnd.choices(cls, k=len(cls)) for k in c]
        if any(y[k] for k in ks) and not all(y[k] for k in ks): d.append(auc(ks, C[a]["s"], y) - auc(ks, C[b]["s"], y))
    d.sort(); return round(auc(pairs, C[a]["s"], y) - auc(pairs, C[b]["s"], y), 3), round(d[int(.025 * len(d))], 3), round(d[int(.975 * len(d))], 3)


out = {"cells": {}, "diffs": {}}
print("cell  pairAUC  AUC(xT)  TP@FM0 TP@FM2 | argmax acc FM miss | sigAUC | trunc err tok")
for c, m in C.items():
    r = {"pair_auc": round(auc(pairs, m["s"], y), 3), "pair_auc_x_target": round(auc(pairs, m["s2"], y), 3),
         "tp_fm0": tp_at(m["s"], 0), "tp_fm2": tp_at(m["s"], 2),
         "acc": round(sum(m["am"](k) == y[k] for k in pairs) / len(pairs), 3), "fm": sum(m["am"](k) and not y[k] for k in pairs),
         "miss": sum(y[k] and not m["am"](k) for k in pairs), "sig_auc": round(auc(sigs, m["sig"], ys), 3),
         "trunc": m["trunc"], "err": m["err"], "tok_median": m["tok"]}
    out["cells"][c] = r
    print(f"{c:5s} {r['pair_auc']:.3f}    {r['pair_auc_x_target']:.3f}    {r['tp_fm0']:3d}    {r['tp_fm2']:3d}   | {r['acc']:.3f} {r['fm']:3d} {r['miss']:3d}     | {r['sig_auc']:.3f}  | {r['trunc']} {r['err']} {r['tok_median']}")
for a, b, lab in [("C2b", "C1b", "input+format (la10)"), ("C2a", "C1a", "input+format (base)"), ("C3", "C2a", "model @full (base)"),
                  ("C3", "C2b", "model @full (la10)"), ("C4", "C1a", "model @compact (base)"), ("C4", "C1b", "model @compact (la10)"),
                  ("C3", "C4", "input+format (Jev)")]:
    if a in C and b in C:
        out["diffs"][f"{a}-{b}"] = boot(a, b); print(f"{lab:24s} {a}-{b}: {out['diffs'][f'{a}-{b}']}")
(D/"p0_result.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
