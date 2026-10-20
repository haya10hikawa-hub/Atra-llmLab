# PREREG_compose.md: chained binary decisions vs direct 5-way, re-scored from existing outputs only (no inference).
# Aggregate only. Writes compose_result.json. usage: compose.py
import json, pathlib, random, collections
L = pathlib.Path(__file__).resolve().parents[3]; B = L/"experiments/realgold"; P0 = L/"experiments/p0_sameinput"; D = pathlib.Path(__file__).parent
cases = {c["case_id"]: c for c in map(json.loads, (B/"dev_real.cases.jsonl").read_text(encoding="utf-8").splitlines())}
folds = json.load(open(B/"folds.json", encoding="utf-8"))
rows = lambda p: {r["case_id"]: r for r in map(json.loads, p.read_text(encoding="utf-8").splitlines())}
K = list(cases); pair = {k: cases[k]["kind"] == "pair" for k in K}
y = {k: cases[k]["label"] in ("same", "work") for k in K}  # pair: same Work; signal: is work
la, c2b, jev = rows(B/"dev/la10/probs.jsonl"), rows(P0/"C2b/answers.jsonl"), rows(B/"dev/jev-latest/answers.jsonl")
e2 = rows(P0/"e12/E2/out.jsonl")
dec = lambda R, k: R[k]["answers"]["decision"]["probabilities"]
tgt = lambda R, k: ((R[k]["answers"].get("target_work") or {}).get("probabilities") or {}).get("W001", 0.0)
mu = lambda d: d["MERGE"] + d["UPDATE"]
# score(k): pair -> P(link to W001); signal -> P(work).  arg(k): argmax decision (bool)
ARMS = {
    "d1_chain": (lambda k: la[k]["is_work"] * la[k]["pairs"]["W001"]["same"] if pair[k] else la[k]["is_work"],
                 lambda k: la[k]["is_work"] >= .5 and (not pair[k] or la[k]["pairs"]["W001"]["same"] > la[k]["p_none"])),
    "d1_direct5": (lambda k: mu(dec(c2b, k)) if pair[k] else 1 - dec(c2b, k)["IGNORE"],
                   lambda k: (max(dec(c2b, k), key=dec(c2b, k).get) in ("MERGE", "UPDATE") and tgt(c2b, k) > .5) if pair[k]
                   else max(dec(c2b, k), key=dec(c2b, k).get) != "IGNORE"),
    "jev_chain": (lambda k: (1 - dec(jev, k)["IGNORE"]) * tgt(jev, k) if pair[k] else 1 - dec(jev, k)["IGNORE"],
                  lambda k: (dec(jev, k)["IGNORE"] < .5 and tgt(jev, k) > .5) if pair[k] else dec(jev, k)["IGNORE"] < .5),
    "jev_direct5": (lambda k: mu(dec(jev, k)) if pair[k] else 1 - dec(jev, k)["IGNORE"],
                    lambda k: (jev[k]["answers"]["decision"]["choice"] in ("MERGE", "UPDATE") and
                               (jev[k]["answers"].get("target_work") or {}).get("choice") == "W001") if pair[k]
                    else jev[k]["answers"]["decision"]["choice"] != "IGNORE"),
}
# compact-only pair comparison (format only, evidence fixed): chain P(select) vs E2 direct 5-way
PAIR_ONLY = {"d1_select_compact": lambda k: la[k]["pairs"]["W001"]["same"], "d1_direct5_compact": lambda k: mu(e2[k]["probs"]["decision"])}


def auc(ks, s):
    pos = [s(k) for k in ks if y[k]]; neg = [s(k) for k in ks if not y[k]]
    return sum((a > b) + .5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))


def thr(ks, s):  # accuracy-max threshold on the training fold
    return max(sorted({s(k) for k in ks}) + [1.01], key=lambda t: sum((s(k) >= t) == y[k] for k in ks))


def xfit_pred(s):  # per kind (pair / signal), fit on the other fold
    out = {}
    for kind in (True, False):
        for tr, te in (("A", "B"), ("B", "A")):
            t = thr([k for k in K if pair[k] == kind and folds[k] == tr], s)
            out.update({k: s(k) >= t for k in K if pair[k] == kind and folds[k] == te})
    return out


def summary(pred, ks):
    return {"acc": sum(pred[k] == y[k] for k in ks) / len(ks), "FM_or_FP": sum(pred[k] and not y[k] for k in ks), "FN": sum(y[k] and not pred[k] for k in ks)}


PR = {a: {"argmax": {k: f[1](k) for k in K}, "xfit": xfit_pred(f[0])} for a, f in ARMS.items()}
res = {"arms": {}, "diffs": {}}
for a, (s, _) in ARMS.items():
    r = {"pair_auc": auc([k for k in K if pair[k]], s), "signal_auc": auc([k for k in K if not pair[k]], s)}
    for m in ("argmax", "xfit"):
        r[m] = {"all": summary(PR[a][m], K), "pair": summary(PR[a][m], [k for k in K if pair[k]]), "signal": summary(PR[a][m], [k for k in K if not pair[k]])}
    res["arms"][a] = r
res["pair_only_compact_auc"] = {a: auc([k for k in K if pair[k]], s) for a, s in PAIR_ONLY.items()}
# paired cluster bootstrap over new-signal threads (all 157 cases)
cl = collections.defaultdict(list)
for k in K: cl[cases[k]["view"]["new_signal"]["thread_key"]].append(k)
cls = list(cl.values()); rnd = random.Random(0)
CMP = [("d1_chain", "d1_direct5"), ("jev_chain", "jev_direct5"), ("d1_chain", "jev_direct5"), ("d1_chain", "jev_chain")]
draws = collections.defaultdict(list)
for _ in range(2000):
    ks = [k for g in rnd.choices(cls, k=len(cls)) for k in g]; pk = [k for k in ks if pair[k]]
    if not any(y[k] for k in pk) or all(y[k] for k in pk): continue
    for a, b in CMP:
        draws[f"{a}-{b}|xfit_acc"].append(sum((PR[a]["xfit"][k] == y[k]) - (PR[b]["xfit"][k] == y[k]) for k in ks) / len(ks))
        draws[f"{a}-{b}|pair_auc"].append(auc(pk, ARMS[a][0]) - auc(pk, ARMS[b][0]))
    draws["compact select-direct5|pair_auc"].append(auc(pk, PAIR_ONLY["d1_select_compact"]) - auc(pk, PAIR_ONLY["d1_direct5_compact"]))
pt = {f"{a}-{b}|xfit_acc": res["arms"][a]["xfit"]["all"]["acc"] - res["arms"][b]["xfit"]["all"]["acc"] for a, b in CMP}
pt |= {f"{a}-{b}|pair_auc": res["arms"][a]["pair_auc"] - res["arms"][b]["pair_auc"] for a, b in CMP}
pt["compact select-direct5|pair_auc"] = res["pair_only_compact_auc"]["d1_select_compact"] - res["pair_only_compact_auc"]["d1_direct5_compact"]
for n, d in draws.items():
    d.sort(); res["diffs"][n] = {"point": round(pt[n], 3), "ci95": [round(d[int(.025 * len(d))], 3), round(d[int(.975 * len(d))], 3)]}
print(json.dumps(res, indent=1, default=lambda x: round(x, 3)))
(D/"compose_result.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
