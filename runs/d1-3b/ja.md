# ja — Japanese paraphrase D ablation

- **Verification:** `VERIFIED_LOCAL`（2026-10-17、学習完了・dev評価をローカル成果物で確認）
- **Model:** LiquidAI/d1-3B
- **Goal:** s85の日本語質問文への感度を改善し、言い換えD単独の効果を切り分ける。
- **Local path:** `experiments/lora/mix-ja`
- **State:** 学習完了（15:01–15:41、840 step、40.2分）。dev評価のみ。封印データは未使用。

## 検証（2026-10-17、ローカル実測、dev = test2）

**目的：** 日本語質問文での精度低下を、言い換えDの学習で減らす。

**変更：** `mix-personal`（s85の元）と同じデータ・混合比・seed 0で、質問セットを`PARA.questions.json`→`PARA2.questions.json`（言い換えD）に変更。

**結果：**

| 指標 | s85 | ja |
|---|---:|---:|
| Formation 正解率（英語質問、in-sample） | 0.858 | 0.854 |
| Formation 正解率（4分割交差検証） | 0.847 | 0.843 |
| 誤マージ（dev0） | 1 | 0 |
| 日本語質問文の正解率 | 0.825（dev2） | 0.843（dev3） |
| Personal 状態の正解率 | 0.653 | **0.520** |
| Personal verdict（`.sp1`閾値） | 0.786 | 0.765 |
| False DONE / 見逃しREQUIRED（`.sp1`） | 3 / 6 | **11 / 13** |
| 余計なREQUIRED（`.sp1`） | 11 | 6 |

注：s85とjaの日本語質問は別セット（PARA[2]とPARA2[3]）で、厳密な同条件比較ではない。

**判断：** 棄却（採用候補にしない）。日本語耐性は改善したが、Personalの重大エラー（False DONE・見逃し）が大きく悪化。

**根拠：** Adapter sha256 `85e577a5fc852135…`、LTT `bd18e36cd50b…`、Personal閾値 `fc84e48e5fda…`、`experiments/lora/mix-ja/{train_meta.json,dev*.scored.json,personal_th.dev.sp1.json}`。

**残課題：** seed 0の1本のみ。seedによるばらつき（[pseed1](pseed1.md)）を下回る差は結論に使えない。頑健性評価（`experiments/robust_v2`）はGPU競合で中断し未完了。

## 作業の制約

- 既存の学習ジョブと子プロセスを確認するまで新規GPUジョブを起動しない。
- 言い換えCは確認用として学習に使用しないという既存の取り決めを維持する。
