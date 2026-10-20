# Blind Gold-audit sheet (local only). 19 pairs both la10 and Jev got wrong + 11 controls both got right, shuffled.
# Hidden from the sheet: gold label, model outputs, correctness, Atra link_hints, case_id/session. Key goes to key.local.json.
import json, pathlib, random
L = pathlib.Path(__file__).resolve().parents[3]; B = L/"experiments/realgold"; O = pathlib.Path(__file__).parent
cases = {c["case_id"]: c for c in map(json.loads, (B/"dev_real.cases.jsonl").read_text(encoding="utf-8").splitlines()) if c["kind"] == "pair"}
ld = lambda a: {r["case_id"]: r["answers"] for r in map(json.loads, (B/"dev"/a/"answers.jsonl").read_text(encoding="utf-8").splitlines())}
la, jv = ld("la10"), ld("jev-latest")
pred = lambda a: (a.get("decision") or {}).get("choice") in ("MERGE", "UPDATE") and (a.get("target_work") or {}).get("choice") == "W001"
ok = lambda m, k: pred(m[k]) == (cases[k]["label"] == "same")
both_wrong = sorted(k for k in cases if not ok(la, k) and not ok(jv, k))
both_right = sorted(k for k in cases if ok(la, k) and ok(jv, k))
rnd = random.Random(20261020)
pick = both_wrong + rnd.sample(both_right, 11); rnd.shuffle(pick)
item = lambda i: f"{i['author']} {i['at'][:16]}: {(i.get('title') + ' / ') if i.get('title') else ''}{i.get('text') or ''}"
md = ["# Gold 監査シート(ブラインド・ローカル専用・共有禁止)", "",
      "各項目で、**新しい信号が既存 Work と同じ Work に属するか**を、下の定義だけに基づいて判定してください。",
      "定義: 同じ成果物・同じ依頼に向けた信号なら同じ Work。同じ人・同じ話題でも、目的や成果物が違えば別 Work。",
      "他の判定者・既存ラベル・モデル出力は見ないでください。", "",
      "回答: `判定: 同じWork / 別Work / 判断不能`、`確信度: 高 / 中 / 低`、一言の理由。", ""]
key = {}
for n, k in enumerate(pick, 1):
    aid = f"Q{n:02d}"; key[aid] = {"case_id": k, "gold": cases[k]["label"], "group": "both_wrong" if k in both_wrong else "control_both_right"}
    v = cases[k]["view"]; w = v["candidate_works"][0] if v["candidate_works"] else None
    md += [f"## {aid}", "", "**既存 Work**", "```"]
    md += [f"タイトル: {w['title']}", f"状態: {w['status']} / {w.get('current_state') or ''}"] + [item(i) for i in w["recent_evidence"]] if w else ["(候補なし)"]
    md += ["```", "**新しい信号**", "```"] + [item(i) for i in v["new_signal"]["items"]] + ["```", "判定: ", "確信度: ", "理由: ", ""]
(O/"audit_sheet.md").write_text("\n".join(md), encoding="utf-8")
(O/"key.local.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
print("items", len(pick), "both_wrong", len(both_wrong), "controls", 11)
