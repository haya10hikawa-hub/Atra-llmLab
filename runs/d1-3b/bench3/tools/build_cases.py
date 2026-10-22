"""Build d1 cases (infer.py rows) for JevBench public, VitaminC test, MASSIVE-en test. usage: build_cases.py <out_dir>"""
import json, os, random, sys
import datasets

OUT, N = sys.argv[1], 1000  # shortcut: 1000-row fixed-seed sample for VitaminC/MASSIVE, full set if time allows
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
JB = os.path.join(HERE, "..", "jevbench_repo", "r", "datasets", "public")


def write(name, rows, gold):
    with open(f"{OUT}/{name}.cases.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(gold, open(f"{OUT}/{name}.gold.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(name, len(rows))


# JevBench public: items already carry a Decision Index question (type/instructions/criteria)
rows, gold = [], {}
for fn in ("original", "hard", "easy"):
    for line in open(f"{JB}/{fn}.jsonl", encoding="utf-8"):
        t = json.loads(line)
        cid = f"{fn}:{t['id']}"
        rows.append({"case_id": cid, "view": t["state"], "questions": {"q": t["question"]}})
        gold[cid] = {"expected": t["expected"], "type": t["question"]["type"], "family": t["family"], "tier": fn,
                     "labels": t["labels"]}
write("jevbench", rows, gold)

# VitaminC (tals/vitaminc) test: claim + evidence -> 3-way
ds = datasets.load_dataset("tals/vitaminc", split="test")
idx = random.Random(13).sample(range(len(ds)), N)
crit = {"SUPPORTS": "The evidence supports the claim.", "REFUTES": "The evidence contradicts the claim.",
        "NOT ENOUGH INFO": "The evidence neither supports nor contradicts the claim."}
rows, gold = [], {}
for i in idx:
    r = ds[i]
    cid = f"vitaminc:{i}"
    rows.append({"case_id": cid, "view": {"claim": r["claim"], "evidence": r["evidence"]},
                 "questions": {"q": {"type": "choice", "instructions": "Does the evidence support the claim?",
                                     "criteria": crit}}})
    gold[cid] = {"expected": r["label"], "type": "choice"}
write("vitaminc", rows, gold)

# MASSIVE-en (mteb/amazon_massive_intent, en test): Laya eval protocol -- gold + 19 sampled labels, shuffled, 20 options
ds = datasets.load_dataset("mteb/amazon_massive_intent", "en", split="test")
labels = sorted(set(ds["label"]))
rng = random.Random(13)
rows, gold = [], {}
for i in rng.sample(range(len(ds)), min(N, len(ds))):
    r = ds[i]
    opts = [r["label"]] + rng.sample([l for l in labels if l != r["label"]], 19)
    rng.shuffle(opts)
    cid = f"massive-en:{i}"
    rows.append({"case_id": cid, "view": {"utterance": r["text"]},
                 "questions": {"q": {"type": "choice", "instructions": "What is the user asking for in `utterance`?",
                                     "criteria": {o: o.replace("_", " ").replace(".", ": ") for o in opts}}}})
    gold[cid] = {"expected": r["label"], "type": "choice"}
write("massive-en", rows, gold)
