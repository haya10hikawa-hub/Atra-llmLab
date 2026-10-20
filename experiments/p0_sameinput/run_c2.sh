#!/bin/bash
# PREREG_p0.md C2a/C2b: d1 on full view + Atra questions (same path as Jev's infer.py run). dev_real only; test7 sealed.
cd "$(dirname "$0")/../.."
export HF_HOME=$PWD/environment/hf PYTHONUTF8=1 CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0
PY=.venv/Scripts/python.exe; D=experiments/p0_sameinput; LOCK=experiments/.gpu0.lock
while [ -e $LOCK ]; do sleep 30; done; echo "p0-c2 $$ $(date +%H:%M)" > $LOCK
for a in C2a C2b; do mkdir -p $D/$a
  if [ $a = C2a ]; then unset D1_LORA; else export D1_LORA=experiments/lora/mix-la10/adapter; fi
  $PY adapters/infer.py d1 experiments/realgold/dev_real.cases.jsonl $D/$a/answers.jsonl > $D/$a/run.log 2>&1
  echo "$a exit $? $(date +%H:%M)"
done; rm -f $LOCK; echo "C2 DONE $(date +%H:%M)"
