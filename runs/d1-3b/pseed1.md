# pseed1 — mix-personal の seed 1 再現

- **Verification:** `VERIFIED_LOCAL`（2026-10-17、ローカル成果物で確認。学習は別セッションが実行）
- **Model:** LiquidAI/d1-3B
- **Local path:** `experiments/lora/mix-pseed1`

**目的：** s85の元である`mix-personal`（seed 0）の結果が、seedを変えても再現するか確かめる。

**変更：** `SEED=1`のみ（データ・混合比・質問・epochは同一、40.5分、Peak VRAM 6.8 GB）。

**結果（dev = test2）：**

| 指標 | seed 0（mix-personal） | seed 1（pseed1） |
|---|---:|---:|
| 識別力 AUC is_work / same / change | 0.999 / 0.998 / 0.861 | 0.997 / 0.996 / 0.844 |
| Formation 正解率（in-sample閾値） | 0.872 | 0.777 |
| 誤った分割 / 棄権 | 11 / 7 | 28 / 18 |
| Formation 4分割交差検証：確率そのまま | 0.865 | 0.756（差 0.109） |
| 同：確率をPlatt較正してから閾値調整 | 0.861 | 0.829（差 0.033） |

同じ較正をv3に適用すると0.832→0.697（棄権44件）に悪化し、較正は一律の解決策ではない。

**判断：** 検証継続。単一seedでのモデル比較は無効とみなす。

**根拠：** Adapter sha256 `d14055fa8ded0cc8…`、`train_meta.json`（seed 1）、`experiments/robust_v2/calib_cv.py`、`experiments/robust_v2/out/calib_cv.json`。

**解釈（INFERENCE）：** 順位付けの力（AUC）はほぼ同じで、差の約7割は確率の目盛りのずれと粗い閾値探索（0.05刻み、誤マージ上限優先）による。s85・ja・v3間の差（0.01〜0.03）はこのばらつきより小さい。

**残課題：** seedは2本のみ。Personal側のseed差、v3 seed 1の結果は未集計。
