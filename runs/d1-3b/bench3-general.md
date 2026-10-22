# bench3-general — LoRA済みd1上位3の汎用ベンチ（JevBench公開 / VitaminC / MASSIVE-en）

- **Verification:** `VERIFIED_LOCAL`（2026-10-20 実行、2026-10-22 記録。生の回答 jsonl は `.gitignore` の方針によりGitHubには含めず、ローカル `experiments/bench3/runs/` に保管）
- **Model:** LiquidAI/d1-3B（revision `051bcc464b01b9f92942b364d9586b0ef5912432`）＋LoRA
- **Local path:** `experiments/bench3`、Adapter は `experiments/lora/mix-<arm>`

**Goal：** Atra向けLoRAが汎用の判断能力を壊していないか（forgetting）を、公開ベンチで確かめる。

**Baseline：** LoRAなしのd1-3B。

**Change：** dev3 Formation正解率（n=532、単体Adapter・argmax）の上位3つ `mix-h2cs05s0`（0.8628, 誤結合5）、`mix-trap0`（0.8628, 誤結合8）、`mix-h2cs05s3`（0.8553, 誤結合6）を評価。

**Prediction：** 事前登録なし（探索的な後付け確認）。反証条件も事前には置いていない。

**Results（argmax正解率、エラー0件）：**

| アーム | JevBench公開231 | VitaminC 1,000 | MASSIVE-en 1,000 | 単純平均 |
|---|---:|---:|---:|---:|
| base d1-3B | 0.749 | 0.816 | 0.912 | 0.826 |
| mix-h2cs05s0 | 0.736 | 0.806 | 0.917 | 0.820 |
| mix-trap0 | 0.745 | 0.809 | 0.913 | 0.822 |
| mix-h2cs05s3 | 0.753 | 0.810 | 0.914 | 0.826 |

JevBench内訳：original（72）は全アーム0.931、easy（48）は全アーム1.000、hard（111）は base 0.523 / h2cs05s0 0.495 / trap0 0.514 / h2cs05s3 0.532。型別は noul（74）が全アーム0.676、score（18）が全アーム0.722。

**Decision：** 3つともbaseと実質同等。悪化は見られず、forgettingは確認されなかった。差は最大でJevBench hardで約3件、VitaminCで約10件、MASSIVE-enで約5件で、単一実行のためノイズの範囲（[seed間ばらつき](pseed1.md)参照）。

**Risks / 注意（INFERENCE・UNKNOWN）：**
- **公式スコアではない。** JevBenchは公開231件（original 72 / hard 111 / easy 48）の正解率のみ。校正・速度・コスト、sealed（非公開）は使っていない。
- VitaminC（`tals/vitaminc` test、seed 13で1,000件抽出）とMASSIVE-en（`mteb/amazon_massive_intent` en test、正解1＋ランダム19の20択、seed 13）の設問文・抽出は本研究側で定めた。Six-group meanの公式設定は定義を確認できず、算出していない。他モデルの公表値とは比較できない。
- 順位付けに使ったdev3は選択用の許可済み用途のみ。
- 3指標は単一実行・単一GPU（RTX 5060 Ti）。

**Next Action：** 比較が必要なら、Six-groupの公式定義を入手してから設定を揃えて再実行。再現手順は `bench3/tools/`（`build_cases.py` → `run.sh` → `score.py`）。ケース本体（問題文）は再配布せず、`build_cases.py` が公開元から再生成する。

**根拠：** `bench3/scores.txt`、`bench3/run.log`。Adapter sha256 は HF `Atra-LLMlab/atra-d1-3b-research`（非公開）のカードに記載。
