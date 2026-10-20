# P1 (2026-10-20): cross-fit threshold / Platt on existing dev_real pair scores. Fit on one fold, apply to the other.
# No inference. Writes p1_result.json (metrics + fitted thresholds/coefs + input sha256). usage: python p1_calib.py
import json, pathlib, math, collections, hashlib
L = pathlib.Path(__file__).resolve().parents[3]; B = L/"experiments/realgold"; OUT = pathlib.Path(__file__).parent/"p1_result.json"
INPUTS = ["dev_real.cases.jsonl", "folds.json"] + [f"dev/{a}/probs.jsonl" for a in ["la10", "t110", "rgA", "rgB"]] + ["dev/jev-latest/answers.jsonl"]
sha = {p: hashlib.sha256((B/p).read_bytes()).hexdigest() for p in INPUTS}
cases = {c["case_id"]: c for c in map(json.loads, (B/"dev_real.cases.jsonl").read_text(encoding="utf-8").splitlines()) if c["kind"] == "pair"}
folds = json.load(open(B/"folds.json", encoding="utf-8"))
ld = lambda a, f: {r["case_id"]: r for r in map(json.loads, (B/"dev"/a/f).read_text(encoding="utf-8").splitlines())}
P = {a: ld(a, "probs.jsonl") for a in ["la10", "t110", "rgA", "rgB"]}; J = ld("jev-latest", "answers.jsonl")
ps = lambda r: list(r["pairs"].values())[0]["same"] if r["pairs"] else 0.0
jd = lambda k: J[k]["answers"]["decision"].get("probabilities") or {}
# score = P(same) for d1 (select harness); P(MERGE)+P(UPDATE) for Jev (reproduces reported AUC 0.904)
S = {"la10": lambda k: ps(P["la10"][k]), "t110": lambda k: ps(P["t110"][k]),
     "rg": lambda k: ps(P["rgB" if folds[k] == "A" else "rgA"][k]), "jev": lambda k: jd(k).get("MERGE", 0) + jd(k).get("UPDATE", 0)}
y = {k: cases[k]["label"] == "same" for k in cases}
F = {f: [k for k in cases if folds[k] == f] for f in "AB"}
lg = lambda p: math.log(max(p, 1e-6) / max(1 - p, 1e-6))


def pick(ks, s, rule):
    """rule 'acc': max accuracy; int n: max TP subject to FM <= n. Ties -> lowest threshold."""
    best = None
    for t in sorted({s(k) for k in ks}) + [1.01]:
        tp = sum(s(k) >= t and y[k] for k in ks); fp = sum(s(k) >= t and not y[k] for k in ks)
        key = sum((s(k) >= t) == y[k] for k in ks) if rule == "acc" else (tp if fp <= rule else -1)
        if best is None or key > best[0]: best = (key, t)
    return best[1]


def platt(ks, s):
    a, b = 1.0, 0.0
    for _ in range(3000):
        ga = gb = 0
        for k in ks:
            x = lg(s(k)); p = 1 / (1 + math.exp(-(a * x + b))); ga += (p - y[k]) * x; gb += p - y[k]
        a -= .01 * ga / len(ks); b -= .01 * gb / len(ks)
    return {"a": a, "b": b}


def decider(s, f):
    if "thr" in f: return lambda k: s(k) >= f["thr"]
    return lambda k: 1 / (1 + math.exp(-(f["a"] * lg(s(k)) + f["b"]))) >= .5


res = {"inputs_sha256": sha, "n_pairs": len(cases), "n_pos": sum(y.values()), "rows": []}
for m, s in S.items():
    rules = {"p>=0.5": lambda tr: {"thr": .5}, "xfit_thr_acc": lambda tr: {"thr": pick(tr, s, "acc")},
             **{f"xfit_thr_FM<={n}": (lambda n: lambda tr: {"thr": pick(tr, s, n)})(n) for n in (0, 1, 2)},
             "xfit_platt_0.5": lambda tr: platt(tr, s)}
    for name, fit in rules.items():
        c = collections.Counter(); fitted = {}
        for tr, te in (("A", "B"), ("B", "A")):
            f = fit(F[tr]); fitted[f"fit_on_{tr}"] = f; dec = decider(s, f)
            for k in F[te]:
                p = dec(k); c["ok"] += p == y[k]; c["fm"] += p and not y[k]; c["miss"] += y[k] and not p
        row = {"model": m, "rule": name, "acc": round(c["ok"] / len(cases), 3), "FM": c["fm"], "miss": c["miss"], "fitted": fitted}
        res["rows"].append(row); print(f"{m:5s} {name:15s} acc {row['acc']:.3f} FM {row['FM']:2d} miss {row['miss']:2d}")
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
