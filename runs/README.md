# 実験レコード

[検索インデックス（CSV）](index.csv)から`run_id`・`model`・`task`・`verification`を検索する。実測を追加したら**実験ごとに新規レコード**を作る。過去の数値を上書きしない。

## 既知の記録（2026-10-17 ローカル成果物で検証）

| 実験 | 状態 | 内容 |
|---|---|---|
| [d1-s85](d1-3b/s85.md) | 現在の基準モデル（test4検証済み） | Formation＋PersonalのLoRA、0.85倍率 |
| [d1-ja](d1-3b/ja.md) | 棄却（Personal重大エラー増） | 日本語言い換えDの影響を切り分け |
| [d1-v3](d1-3b/v3.md) | 棄却（devゲート不合格） | 言い換えD＋状態データsL |
| [d1-pseed1](d1-3b/pseed1.md) | 検証継続 | seed違い再現。seed差＞モデル間差 |
| [d1-trap0 / ens](d1-3b/trap0.md) | test6 最終評価済み（Formation で Jev 以上） | 誤り分解・リンク罠データ train8・2 モデル ensemble |

## 記録規約

- 事前：仮説、元のBaseline、反証可能な予測、データの分割、費用・品質の成功条件を明示する。
- 事後：実測、無効Run、変化量、棄却理由、未検証事項を残す。
- 原本のファイル構造やモデルAdapterを勝手に移動しない。実コード移管時は別Commitとする。
- 生成Goldと人間Gold、単発判断とFull Replay、開発データと封印データを常に区別する。

