# 実験レコード

[検索インデックス（CSV）](index.csv)から`run_id`・`model`・`task`・`verification`を検索する。実測を追加したら**実験ごとに新規レコード**を作る。過去の数値を上書きしない。

## 既知の記録（2026-10-17 ローカル成果物で検証）

| 実験 | 状態 | 内容 |
|---|---|---|
| [d1-s85](d1-3b/s85.md) | 現在の基準モデル（test4検証済み） | Formation＋PersonalのLoRA、0.85倍率 |
| [d1-ja](d1-3b/ja.md) | 棄却（Personal重大エラー増） | 日本語言い換えDの影響を切り分け |
| [d1-v3](d1-3b/v3.md) | 棄却（devゲート不合格） | 言い換えD＋状態データsL |
| [d1-pseed1](d1-3b/pseed1.md) | 検証継続 | seed違い再現。seed差＞モデル間差 |
| [g12-gate](gemma-4-12b/g12-gate.md) | 完了（12B 採用候補、26B は量子化で不合格） | Gemma-4 zero-shot と GGUF 量子化の関門（実データ AUC 0.91–0.935） |
| [g12L2](gemma-4-12b/g12L2.md) | 完了（実データで zero-shot 以上にならず） | Gemma-4-12B への LoRA（Formation+Personal）。dev3 は改善、dev_real は同等以下 |
| [g12L2-replay](gemma-4-12b/g12L2-replay.md) | 完了（Jev 並み基準 4/5、誤検出 REQUIRED 8 > 6） | dev3 Full Replay と封印 test8s の 1 回評価（合成のみ） |

## 記録規約

- 事前：仮説、元のBaseline、反証可能な予測、データの分割、費用・品質の成功条件を明示する。
- 事後：実測、無効Run、変化量、棄却理由、未検証事項を残す。
- 原本のファイル構造やモデルAdapterを勝手に移動しない。実コード移管時は別Commitとする。
- 生成Goldと人間Gold、単発判断とFull Replay、開発データと封印データを常に区別する。

