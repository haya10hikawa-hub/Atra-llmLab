# g12L2-replay — Full Formation Replay（dev3）と封印 test8s の 1 回評価

- **Verification:** `VERIFIED_LOCAL`（2026-10-24 / 25、llama-server、GPU 1 枚、外部 API なし）
- **Model:** Gemma-4-12B-it QAT Q4_0 + LoRA g12L2（R1）。対照：R0 = zero-shot（argmax）、R0c = zero-shot + dev3 の閾値（in-sample で甘い）。
- **Goal:** Atra の Replay（Atra エンジンは無変更。`SERVE_SCRIPT` で serve だけ差し替え）で Jev に並ぶかを測る。
- **Baseline:** jev-latest、jev-preview、d1 ens-fix1（同一 dev3 の Replay）。
- **Prediction（事前登録）:** 「Jev に並ぶ」= exact ≥ .752、mixed ≤ 12、false merge ≤ 12、見逃し REQUIRED ≤ 13、誤検出 REQUIRED ≤ 6。

## Results：dev3 Full Replay（48 シナリオ、gold works 179）
| 構成 | exact | mixed | duplicated | false merge | 判定正解率 | 見逃し REQUIRED（/51） | 誤検出 REQUIRED |
|---|---:|---:|---:|---:|---:|---:|---:|
| jev-latest | .782 | 10 | 11 | 10 | .880 | 13 | 4 |
| jev-preview | .821 | 11 | 6 | 12 | .917 | 9 | 3 |
| d1 ens-fix1 | .799 | 9 | 14 | 9 | .897 | 7 | 7 |
| **R1（LoRA + QAT）** | **.832** | **5** | 15 | **5** | .882 | **7** | 8 |
| R0（zero-shot） | .179 | 18 | 5 | 20 | .605 | 4 | 37 |
| R0c（zero-shot + 閾値） | .296 | 15 | 12 | 16 | .648 | 5 | 38 |

R1 は 5 項目中 4 項目を満たす。**不合格は誤検出 REQUIRED（8 > 6）**。zero-shot（R0/R0c）は確率が飽和して Work を形成できず、大きく不合格。

## Results：封印 test8s（合成 44 シナリオ、1 回のみ・消費済み）
事前登録（2026-10-25）：主指標は手がかりなしの MERGE 再現率（MERGE 正解 27 件のうち ≥ 19 件で合格、≤ 13 件で不合格）、false merge ≤ 8。閾値の調整なし（raw argmax）。
| 指標 | 値 |
|---|---|
| ケース単位 accuracy | .939（124/132）、false merge 0、false split 4、wrong ignore 3、spurious update 1 |
| Replay | exact .919（formed 87 / gold 86）、mixed 0、duplicated 4、false split pairs 7/34、判定正解率 .947、見逃し REQUIRED 0/44、誤検出 REQUIRED 0 |
主基準は、誤答合計 8 件から再現率 ≥ 20/27（0.74）と下限で言えるため合格（件数の内訳は確認していない）。false merge 0 も合格。

## Decision
R1 は同系統の合成データ上で Jev・d1 最良と同等以上。ただし「Jev に並ぶ」は dev3 では 4/5 で、誤検出 REQUIRED が残課題。

## Risks / 未検証
- dev3・test8s ともに合成で、ラベルは Claude 作成（人手 Gold ではない）。LoRA も同系統の合成で学習したため、同分布に近い評価。
- test8s には Jev・d1 の基準値がなく、「Jev を超える／並ぶ」の主張は test8s からはできない。
- 実データ（dev_real）では LoRA は zero-shot より良くない（[g12L2](g12L2.md)）。実データの Replay は未実施。
- 単一 seed・1 回実行。test8s は再評価しない（完了マーカーで防止）。封印データの正解表・個別誤答は公開しない。

## Next Action
誤検出 REQUIRED の削減（別エージェント）。公開用 Adapter の来歴・ライセンス審査。
