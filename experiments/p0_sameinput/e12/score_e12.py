# PREREG_e12.md scorer. Aggregate only (no case text). Writes e12_result.json. usage: score_e12.py
import json, pathlib, random, collections, statistics, math
L = pathlib.Path(__file__).resolve().parents[3]; B = L/"experiments/realgold"; D = pathlib.Path(__file__).parent
cases = {c["case_id"]: c for c in map(json.loads, (B/"dev_real.cases.jsonl").read_text(encoding="utf-8").splitlines()) if c["kind"] == "pair"}
folds = json.load(open(B/"folds.json", encoding="utf-8"))
pairs = list(cases); y = {k: cases[k]["label"] == "same" for k in pairs}
rows = lambda p: {r["case_id"]: r for r in map(json.loads, p.read_text(encoding="utf-8").splitlines())}
FORMAT = {"R-C1b": "select", "E1": "select", "E2": "formation", "R-C2b": "formation"}
R = {c: rows(D/c/"out.jsonl") for c in FORMAT}


def score(c, k, kind="main"):
    p = R[c][k]["probs"]
    if FORMAT[c] == "select": return p["select"]["W001"]
    d = p["decision"]; mu = d["MERGE"] + d["UPDATE"]
    return {"main": mu, "mu_vs_create": mu / max(mu + d["CREATE"], 1e-9), "target": p["target_work"]["W001"]}[kind]


def argmax_pos(c, k):
    p = R[c][k]["probs"]
    if FORMAT[c] == "select": return p["select"]["W001"] > p["select"]["NONE"]
    d = p["decision"]; return max(d, key=d.get) in ("MERGE", "UPDATE") and p["target_work"]["W001"] > p["target_work"]["NONE"]


def auc(ks, s):
    pos = [s(k) for k in ks if y[k]]; neg = [s(k) for k in ks if not y[k]]
    return sum((a > b) + .5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))


def tp_at(s, kfm, ks=pairs):
    srt = sorted(ks, key=s, reverse=True); tp = fp = best = 0; top = set()
    for i, k in enumerate(srt):
        tp += y[k]; fp += not y[k]
        if fp <= kfm and (i + 1 == len(srt) or s(srt[i + 1]) < s(k)): best, top = max(best, tp), set(srt[:i + 1])
    return best, top


def pick(ks, s, rule):
    best = None
    for t in sorted({s(k) for k in ks}) + [1.01]:
        tp = sum(s(k) >= t and y[k] for k in ks); fp = sum(s(k) >= t and not y[k] for k in ks)
        key = sum((s(k) >= t) == y[k] for k in ks) if rule == "acc" else (tp if fp <= rule else -1)
        if best is None or key > best[0]: best = (key, t)
    return best[1]


def xfit(s, rule):
    c = collections.Counter()
    for tr, te in (("A", "B"), ("B", "A")):
        t = pick([k for k in pairs if folds[k] == tr], s, rule)
        for k in pairs:
            if folds[k] == te: p = s(k) >= t; c["fm"] += p and not y[k]; c["fn"] += y[k] and not p
    return {"FM": c["fm"], "FN": c["fn"]}


q = lambda xs, f: round(sorted(xs)[min(len(xs) - 1, int(f * len(xs)))], 4)
res = {"validity": {}, "cells": {}, "effects": {}, "concentration": {}}
# parity gate: re-runs must reproduce the existing C1b / C2b scores
la10 = rows(B/"dev/la10/probs.jsonl"); c2b = rows(D.parent/"C2b/answers.jsonl")
old = {"R-C1b": lambda k: la10[k]["pairs"]["W001"]["same"],
       "R-C2b": lambda k: (lambda d: d["MERGE"] + d["UPDATE"])(c2b[k]["answers"]["decision"]["probabilities"])}
for c, f in old.items():
    res["validity"][f"{c}_max_abs_diff_vs_existing"] = round(max(abs(score(c, k) - f(k)) for k in pairs), 5)
for c in FORMAT:
    rr = R[c].values(); lat = [r["latency_ms"] for r in rr]
    res["validity"][c] = {"n": len(R[c]), "errors": sum(bool(r["error"]) for r in rr), "truncated": sum(bool(r.get("truncated")) for r in rr),
                          "tokens_median": statistics.median(r.get("input_tokens") or 0 for r in rr), "lat_p50_ms": q(lat, .5), "lat_p95_ms": q(lat, .95)}
print(json.dumps(res["validity"], indent=1))
for c in FORMAT:
    s = lambda k, c=c: score(c, k)
    r = {"auc": round(auc(pairs, s), 3), "auc_foldA": round(auc([k for k in pairs if folds[k] == "A"], s), 3),
         "auc_foldB": round(auc([k for k in pairs if folds[k] == "B"], s), 3),
         **{f"tp_fm{n}": tp_at(s, n)[0] for n in (0, 2, 5)},
         "argmax_acc": round(sum(argmax_pos(c, k) == y[k] for k in pairs) / len(pairs), 3),
         "argmax_FM": sum(argmax_pos(c, k) and not y[k] for k in pairs), "argmax_FN": sum(y[k] and not argmax_pos(c, k) for k in pairs),
         "pos_p10_p50_p90": [q([s(k) for k in pairs if y[k]], f) for f in (.1, .5, .9)],
         "neg_p50_p90_max": [q([s(k) for k in pairs if not y[k]], f) for f in (.5, .9, .999)],
         "xfit_acc": xfit(s, "acc"), "xfit_FM<=2": xfit(s, 2)}
    if FORMAT[c] == "formation":
        r["auc_secondary_mu_vs_create"] = round(auc(pairs, lambda k: score(c, k, "mu_vs_create")), 3)
        r["auc_secondary_target"] = round(auc(pairs, lambda k: score(c, k, "target")), 3)
        r["mean_abstain_ignore_mass"] = round(statistics.mean(R[c][k]["probs"]["decision"]["ABSTAIN"] + R[c][k]["probs"]["decision"]["IGNORE"] for k in pairs), 3)
    res["cells"][c] = r; print(c, json.dumps(r))
# effects: paired cluster bootstrap over new-signal threads
cl = collections.defaultdict(list)
for k in pairs: cl[cases[k]["view"]["new_signal"]["thread_key"]].append(k)
cls = list(cl.values()); A = {c: (lambda c: lambda k: score(c, k))(c) for c in FORMAT}
EFF = {"evidence|select (E1-C1b)": {"E1": 1, "R-C1b": -1}, "evidence|formation (C2b-E2)": {"R-C2b": 1, "E2": -1},
       "format|compact (E2-C1b)": {"E2": 1, "R-C1b": -1}, "format|full (C2b-E1)": {"R-C2b": 1, "E1": -1},
       "interaction (C2b-E2-E1+C1b)": {"R-C2b": 1, "E2": -1, "E1": -1, "R-C1b": 1}, "both (C2b-C1b)": {"R-C2b": 1, "R-C1b": -1}}
rnd = random.Random(0); draws = collections.defaultdict(list)
for _ in range(2000):
    ks = [k for g in rnd.choices(cls, k=len(cls)) for k in g]
    if all(y[k] for k in ks) or not any(y[k] for k in ks): continue
    a = {c: auc(ks, A[c]) for c in FORMAT}
    for n, w in EFF.items(): draws[n].append(sum(v * a[c] for c, v in w.items()))
for n, w in EFF.items():
    d = sorted(draws[n]); pt = sum(v * res["cells"][c]["auc"] for c, v in w.items())
    res["effects"][n] = {"point": round(pt, 3), "ci95": [round(d[int(.025 * len(d))], 3), round(d[int(.975 * len(d))], 3)]}
    print(f"{n:30s} {res['effects'][n]}")
# concentration: who leaves / enters the FM<=2 top set relative to R-C1b
def feat(k):
    v = cases[k]["view"]; w = v["candidate_works"][0]; ns = v["new_signal"]
    loss = len(w["recent_evidence"]) > 3 or any(len(i.get("text") or "") > 200 for i in w["recent_evidence"]) or any(len(i.get("text") or "") > 600 for i in ns["items"])
    return {"hint": ",".join(sorted({h.split(":")[0] for h in w["link_hints"]})) or "none", "owned": ns["thread_already_owned_by_work"] == w["work_id"], "compact_loses_text": loss}
base_top = tp_at(A["R-C1b"], 2)[1]
for c in ("E1", "E2", "R-C2b"):
    top = tp_at(A[c], 2)[1]
    lost_pos = [k for k in base_top - top if y[k]]; new_neg = [k for k in top - base_top if not y[k]]
    agg = lambda ks: {f: dict(collections.Counter(str(feat(k)[f]) for k in ks)) for f in ("hint", "owned", "compact_loses_text")}
    res["concentration"][c] = {"pos_lost_from_C1b_top": len(lost_pos), "pos_lost_feat": agg(lost_pos), "pos_gained": sum(y[k] for k in top - base_top),
                               "neg_top_new": len(new_neg), "neg_top_new_feat": agg(new_neg)}
    print(c, json.dumps(res["concentration"][c], ensure_ascii=False))
res["slices_auc"] = {}
for f in ("hint", "owned", "compact_loses_text"):
    for val in sorted({str(feat(k)[f]) for k in pairs}):
        ks = [k for k in pairs if str(feat(k)[f]) == val]
        if any(y[k] for k in ks) and not all(y[k] for k in ks):
            res["slices_auc"][f"{f}={val}"] = {"n": len(ks), "pos": sum(y[k] for k in ks), **{c: round(auc(ks, A[c]), 3) for c in FORMAT}}
print(json.dumps(res["slices_auc"], ensure_ascii=False))
(D/"e12_result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
