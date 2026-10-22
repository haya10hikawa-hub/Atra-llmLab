"""Argmax accuracy per benchmark/arm (+ JevBench by type/tier). usage: score.py <bench3_dir>"""
import json, sys, os, collections
D = sys.argv[1]
def pred(a):
    if a["type"] == "noul": return "yes" if a["noul"] >= 0.5 else "no"
    if a["type"] == "choice": return a["choice"]
    return max(a["probabilities"], key=a["probabilities"].get)
res = {}
for arm in sorted(os.listdir(f"{D}/runs")):
    for b in ("jevbench", "vitaminc", "massive-en"):
        p = f"{D}/runs/{arm}/{b}.answers.jsonl"
        if not os.path.exists(p): continue
        gold = json.load(open(f"{D}/cases/{b}.gold.json", encoding="utf-8"))
        ok = collections.defaultdict(lambda: [0, 0]); err = 0
        for l in open(p, encoding="utf-8"):
            r = json.loads(l); g = gold[r["case_id"]]
            hit = False
            if r["answers"]: hit = pred(r["answers"]["q"]) == str(g["expected"])
            else: err += 1
            for k in ("all", g.get("tier"), g.get("type") if b == "jevbench" else None):
                if k: ok[k][0] += hit; ok[k][1] += 1
        res[(arm, b)] = {k: f"{v[0]/v[1]:.3f} ({v[0]}/{v[1]})" for k, v in ok.items()} | {"errors": err}
for (arm, b), v in res.items(): print(arm, b, v)
