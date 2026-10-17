# Atra-llmLab

Atraの**Formation / Personal判断**について、**Jev以上の絶対品質**と**判断品質あたりの推論コスト最小化**を検証する研究リポジトリ。

本リポジトリは製品コードの所有者ではない。AtraのUX、Decision Contract、WorkStore、Validator、Approvalは[Atra-workunitOS](https://github.com/haya10hikawa-hub/Atra-workunitOS)が所有する。実験から本番への自動反映はしない。

## 入口

| 探すもの | 場所 |
|---|---|
| 実験ID・モデル・状態から探す | [runs/index.csv](runs/index.csv) |
| 実験の経緯・結果・未検証事項 | [runs/README.md](runs/README.md) |
| 精度・コストの測定規約 | [docs/measurement.md](docs/measurement.md) |
| Atraの契約と採用手順 | [docs/adoption.md](docs/adoption.md) |
| Agentへの作業規約 | [AGENTS.md](AGENTS.md) |

## ディレクトリ

```text
runs/
  index.csv        実験の検索用索引（1実験=1行）
  d1-3b/           d1実験の経緯（s85 / ja / v3は報告ベース）
docs/
  measurement.md   評価・測定の不変条件
  adoption.md      Atraへの採用境界
```

**必要になるまで追加しない：** 新しい共通Harness、モデルRegistry、Web UI、CI GPUジョブ、サービスAPI、Submodule。

既存ローカル実験の`adapters/`、`evaluators/`、`experiments/`、`reports/`は、実物を確認してから**相対パスを壊さず**取り込む。空ディレクトリを先回りして作らない。

## 現状と出典

初期のs85 / ja / v3記録は**2026-10-17に提供されたAgent Handoffの転記**であり、モデル・ログ・評価データはこのRepoに含まれていない。`runs/index.csv`の`verification=REPORTED_ONLY`を確認すること。数値はClaude生成の合成データに対するもの。Jevに対する直接優位や実務性能の証明ではない。

## 関連リポジトリ

- [Atra-workunitOS](https://github.com/haya10hikawa-hub/Atra-workunitOS) — 製品・契約・実装。初期の参照main: [`0c8aedc`](https://github.com/haya10hikawa-hub/Atra-workunitOS/commit/0c8aedc49b2ff8249ec127783229424156c81b14)（2026-10-17確認）。実験ごとに必ず使用SHAを別途固定する。
- [llm-gpu-tuning](https://github.com/haya10hikawa-hub/llm-gpu-tuning) — 汎用GPU/LLM高速化と測定規約。本RepoはAtra固有の品質・コストを扱い、汎用GPU改善はここで重複管理しない。

## 研究から採用まで

仮説を記録 → 対照を含む再現可能な実験 → 品質・コスト測定 → 棄却または採用候補化 → PM判断 → Atra側の独立PR。**合格しない研究結果を本番に流さない。**

