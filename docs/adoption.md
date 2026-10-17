# Atraとの接続・採用境界

## Ownership

- **Atra-workunitOS**：製品方向、UX、Formation/Personalの意味・契約、Evidence、Validator、WorkStore、本番SLC。
- **Atra-llmLab**：モデル学習、Prompt/GEPA/LoRA/Pairwise、独立評価、計測、実験の採否記録。
- **llm-gpu-tuning**：GPUやモデルに汎用的なカーネル・ランタイム・測定改善。

## 契約参照

初期に参照したAtra mainは[`0c8aedc49b2ff8249ec127783229424156c81b14`](https://github.com/haya10hikawa-hub/Atra-workunitOS/commit/0c8aedc49b2ff8249ec127783229424156c81b14)。**これは固定参照であり、本番の常時同期ではない。** 実験ごとにcommitと該当ファイルのhashを記録する。

- [Decision Contract](https://github.com/haya10hikawa-hub/Atra-workunitOS/blob/main/tools/formation-eval/contract.mjs)
- [Preprocessing / Candidates](https://github.com/haya10hikawa-hub/Atra-workunitOS/blob/main/tools/formation-eval/preprocess.mjs)
- [Validation](https://github.com/haya10hikawa-hub/Atra-workunitOS/blob/main/tools/formation-eval/validator.mjs)
- [Personal judgment](https://github.com/haya10hikawa-hub/Atra-workunitOS/blob/main/tools/formation-eval/slcPersonal.mjs)
- [Replay and scoring](https://github.com/haya10hikawa-hub/Atra-workunitOS/blob/main/tools/formation-eval/evaluate.mjs)
- [Product State](https://github.com/haya10hikawa-hub/Atra-workunitOS/blob/main/PRODUCT_STATE.md)

## Production gate

1. 人間正解のあるデータでJevと同条件比較。重大エラーが悪化しないこと。
2. 同じSnapshotでFull Replay、Evidence整合性、障害・ABSTAIN処理を検証する。
3. GPU秒・電力・VRAM・エンドツーエンド遅延・運用費を再現可能な形で記録する。
4. PMが採用を承認した場合のみ、**Atra側の独立PR**としてAdapterの最小差分を導入し、E2E・Rollbackを検証する。

**しないこと：** LabからAtra本番mainへの自動デプロイ、Figma/UXの変更、Atraの契約の変更、Git Submodule、秘密データのコピー。

