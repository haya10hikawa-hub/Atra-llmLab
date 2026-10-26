# g12-gate — Gemma-4 zero-shot gate と量子化の関門

- **Verification:** `VERIFIED_LOCAL`（2026-10-23、dev_real はローカルのみ。AWS には case_id/view/questions だけを置き、終了後に削除）
- **Model:** google/gemma-4-12B-it、google/gemma-4-26B-A4B-it（どちらも公開・非ゲート、HF メタデータ上 Apache-2.0）
- **Goal:** 現行（d1-3B、Qwen3.5 LoRA）を超えるローカル推論可能なオープンウェイトがあるかを、zero-shot で測る。次に、ローカル配備用の量子化（GGUF）で劣化しないかを測る。
- **Baseline:** d1 LoRA 各介入 AUC 0.83–0.88、Qwen3.5-4B/9B LoRA 0.85–0.90、Jev 0.899、Qwen3.6-27B zero-shot 0.936。
- **Prediction（事前）:** 12B/26B の zero-shot は 0.85 を超える。量子化の許容は zero-shot から 0.02 以内。
- **Change:** select-form（NONE + 候補 Work に対する 1 回の next-token readout）、Gemma の chat template（`PROMPT_STYLE=gemma`）。回答 prefix は空（`Answer: ` では label mass 0.26–0.31、空で 0.97–1.0）。

## Results（dev_real = 実データ 157 件、ペア AUC。CI は ±0.08 程度。データ・個別結果は非公開）
| 構成 | pair AUC |
|---|---:|
| 12B zero-shot bf16 | 0.913（prefix `Answer:` で 0.926） |
| 26B-A4B zero-shot bf16 | 0.925 |
| 12B QAT Q4_0 GGUF（6.5 GiB、Google 公式） | 0.926（合格） |
| 12B Q8_0 GGUF | 0.935（合格） |
| 26B-A4B QAT Q4_0 GGUF（13.45 GiB） | 0.899（**不合格**、損失 > 0.02） |

## Decision
12B を採用候補にする（26B は量子化で不合格）。zero-shot でも従来の LoRA 腕より実データで高い、というのが次の LoRA 検証（[g12L2](g12L2.md)）の前提。

## Risks / 未検証
- 単一 seed、CI ±0.08。0.03 未満の差は結論に使えない。
- JevBench の公式スコアではない（public-231 の proxy のみ。Calibration の式は不明）。
- 以前「JevBench の改善（49→67）は LoRA の効果」と報告したのは誤りで、実際は Gemma base の効果だった（LoRA は QAT で −5.5、Q8 で −1.0）。訂正済み。

## Next Action
[g12L2](g12L2.md)（LoRA 追加の要否）。
