#!/bin/bash
# usage: run.sh  -- base d1 + top-3 dev3 LoRAs x {jevbench,vitaminc,massive-en}
cd "$(dirname "$0")/../../.."
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0
PY=.venv/Scripts/python.exe
for arm in base mix-h2cs05s0 mix-trap0 mix-h2cs05s3; do
  for b in jevbench vitaminc massive-en; do
    out=experiments/bench3/runs/$arm; mkdir -p $out
    [ -s $out/$b.answers.jsonl ] && continue
    if [ $arm = base ]; then unset D1_LORA; else export D1_LORA=experiments/lora/$arm/adapter; fi
    echo "$(date -Is) $arm $b start"
    $PY adapters/infer.py d1 experiments/bench3/cases/$b.cases.jsonl $out/$b.answers.jsonl || echo "FAIL $arm $b"
  done
done
echo "$(date -Is) BENCH3 DONE"
