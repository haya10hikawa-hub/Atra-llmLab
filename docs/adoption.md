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

## 公開方針（PM決定：2026-10-17）

**研究は最大限オープン、実務データと本番の競争資産はクローズド。** 本Repoは公開研究の置き場とし、Atra本体のソース・運用・顧客データの公開許可を意味しない。

| 原則公開 | 公開前に個別審査 | 非公開 |
|---|---|---|
| 研究目的・手法・一般化した学習/評価コード・実験設定・再現手順・集計結果・失敗記録 | 合成データ、第三者のモデル/データ由来の派生物、研究用AdapterやCheckpoint | 実務Signal/Evidence、顧客・個人情報、人手付けした実務Gold、封印評価データ、本番Prompt/閾値/Adapter、認証情報 |

**公開前の最低確認：**

1. データの権利・同意・教師APIの利用規約・元モデルのライセンスを確認する。Apache-2.0のRepositoryライセンスが、第三者由来のモデルやデータにも自動適用されるわけではない。
2. 機密情報・個人名・ローカル絶対パス・識別子・実務引用・再識別の手掛かりを除外する。必要なら公開用の合成データだけを別に用意する。
3. 公開したベンチマークは学習と独立しているか、評価済み・調整済みかを明記する。**封印データ、正解ラベル、個別誤答を公開して評価の独立性を壊さない。**
4. 公開用研究Adapterは権利とデータ由来が確認できたものに限る。本番運用のAdapterと設定を転記しない。
5. 公開済みのGit履歴は削除しても第三者のコピーに残り得るため、コミット**前**に差分を確認する。判断に迷うものは非公開としてPMに確認する。

公開判断と本番採用判断は別。研究が再現可能でも、Atraの実務品質を実証したことにはならない。

## Production gate

1. 人間正解のあるデータでJevと同条件比較。重大エラーが悪化しないこと。
2. 同じSnapshotでFull Replay、Evidence整合性、障害・ABSTAIN処理を検証する。
3. GPU秒・電力・VRAM・エンドツーエンド遅延・運用費を再現可能な形で記録する。
4. PMが採用を承認した場合のみ、**Atra側の独立PR**としてAdapterの最小差分を導入し、E2E・Rollbackを検証する。

**しないこと：** LabからAtra本番mainへの自動デプロイ、Figma/UXの変更、Atraの契約の変更、Git Submodule、秘密データのコピー。

