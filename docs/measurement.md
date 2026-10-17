# 品質・推論コストの測定規約

目的：Jev以上の**絶対品質**を目指し、安全条件を満たす候補の中で**判断1件に必要な総計算量**を減らす。

## 品質指標（分離して報告）

- Formation：Accuracy、False Merge / False Split / Missed UPDATE、ABSTAIN、Evidence整合性。
- Personal：REQUIREDのRecall、False DONE、Spurious REQUIRED、担当者・状態・根拠。
- Atra Full Replay：最終的なWork同一性・重複・見落とし。単発Accuracyでは代替不可。
- Jev / Opusの比較は**同一Snapshot・候補・契約・正解・採点条件**でのみ優劣を述べる。合成Goldは人間Goldではない。

## 性能指標

- **主指標：** 完了した正しい判断あたりのGPU秒、p50/p95遅延、総Forward回数。
- **補助：** Peak VRAM、Joules/decision（測定可能なとき）、判断/s、バッチと入力長の分布。
- コストには前処理、関係抽出、追加質問、失敗・再試行を含める。d1をtokens/sで評価しない。
- JevのAPI費用とGPUコストを比べる場合、電力単価・ハード償却・測定の価格基準を区別する。

## 測定が信用できる条件

- GPUを一度に1ジョブ。稼働中の`ja/v3`を止めたり二重起動したりしない。
- GPU利用とCPU fallback、温度、VRAM、モデル/LoRAスケール、Batch、精度、driver/CUDA/Torchバージョンを記録。
- 初回のロード・カーネル初期化は定常推論時間から分離。比較中は対照を定期的に挟む。
- 同じ問いを複数回評価し、差の大きさ・ばらつき・サンプル件数を記録。単一事例で結論を出さない。
- 失敗時は`FAILED`/`INVALID`として保存。エラーやOOMを正常な遅延として集計しない。
- 予測とKill条件を先に登録する。結果に合わせて合格基準を変更しない。
- Dataset・Gold・Contract・Model・Adapter・Threshold・Codeのハッシュを実験単位で固定する。

## 禁止

既評価test3/test4での再最適化、test5の無断開封、合成データを根拠にした実務性能の断言、プライベートEvidenceの無断コミット・送信。

参照：[llm-gpu-tuningの共通規則](https://github.com/haya10hikawa-hub/llm-gpu-tuning/blob/master/AGENTS.md)、[AtraのFormation評価](https://github.com/haya10hikawa-hub/Atra-workunitOS/blob/main/tools/formation-eval/evaluate.mjs)。

