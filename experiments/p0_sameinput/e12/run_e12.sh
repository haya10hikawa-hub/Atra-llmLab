#!/bin/bash
# PREREG_e12.md: d1 la10 on 4 cells via run_cell.py. R-C1b / R-C2b are parity re-runs of the existing C1b / C2b.
cd "$(dirname "$0")/../../.."
export HF_HOME=$PWD/environment/hf PYTHONUTF8=1 CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 D1_LORA=experiments/lora/mix-la10/adapter
PY=.venv/Scripts/python.exe; D=experiments/p0_sameinput/e12; LOCK=experiments/.gpu0.lock
[ -e $LOCK ] && { echo "GPU LOCKED by $(cat $LOCK); abort"; exit 1; }
echo "p0-e12 $$ $(date +%H:%M)" > $LOCK
for cell in "R-C1b compact select" "E1 full select" "E2 compact formation" "R-C2b full formation"; do
  set -- $cell; mkdir -p $D/$1
  $PY $D/run_cell.py $2 $3 $D/$1/out.jsonl > $D/$1/run.log 2>&1; echo "$1 exit $? $(date +%H:%M:%S)"
done; rm -f $LOCK; echo "E12 DONE $(date +%H:%M:%S)"
