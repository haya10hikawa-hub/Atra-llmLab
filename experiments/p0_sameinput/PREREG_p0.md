# PREREG P0 — 同一入力比較: Jev と d1 の差を「入力情報」「判定形式」「モデル能力」に分解する
2026-10-20 に、新しい推論を実行する前に書いた。dev_real のみを使う(test7 は開封しない)。学習・閾値変更・本番変更はしない。

## 背景(既知の事実)
- 既存の比較では、d1 と Jev の条件が違う。
  - d1: `adapters/pairwise.py`、`PAIRWISE_SELECT=1`。compact view(候補 evidence 3件×200字、signal 600字)に対し、「候補 W001 か NONE か」の select で答える。
  - Jev: `adapters/infer.py`。full engine view と、Atra の質問(`decision` 5択 + `target_work`)で答える。
- pair AUC: la10 0.862、Jev 0.904。差 +0.042、cluster bootstrap の 95% CI は [-0.021, +0.117]。
- 正例の回収数(FM ≤ 2): la10 17/53、Jev 35/53。in-sample の閾値掃引による値。
- P1(`p1/`)の結論: 単調な閾値補正では、FM ≤ 2 の域の差は埋まらない。

## セル(2×2 + 1)
入力と判定形式は同時に変わる。分けるにはコードの新設が必要なので、今回は分けない。

| セル | モデル | 入力・判定形式 | 状態 |
|---|---|---|---|
| C1a | d1 base | compact / select | 既存(`realgold/dev/base`) |
| C1b | d1 + la10 | compact / select | 既存(`realgold/dev/la10`) |
| C2a | d1 base | full view / Atra の 5択 + target | **今回実行** |
| C2b | d1 + la10 | full view / Atra の 5択 + target | **今回実行**(参考) |
| C3 | Jev-latest | full view / Atra の 5択 + target | 既存(`realgold/dev/jev-latest`) |
| C4 | Jev-latest | compact / select | **保留**(送信権限・機密性・API 規約の確認後) |

- C2 の実行コマンドは、Jev と同じ経路にする: `infer.py d1 dev_real.cases.jsonl` で、`questions` は case 内のものを使う。
- C2b の la10 は select と pairwise の形式で学習したアダプタなので、C2 の形式では学習分布の外になる。主比較には **C2a**(未調整同士)を使い、C2b は参考にとどめる。

## スコアと指標(全セル共通、`score_p0.py` で計算)
- pair score(主): full 形式では P(MERGE) + P(UPDATE)。select 形式では P(same=W001)。
- pair score(副): full 形式で (P(MERGE) + P(UPDATE)) × P(target=W001)。
- signal score: full 形式では 1 - P(IGNORE)。select 形式では is_work。副指標として扱う(n=51)。
- 指標:
  - pair AUC。
  - セル間の差の 95% CI。new-signal thread 単位の cluster bootstrap(75 クラスタ、2000 回、seed 0)。
  - 正例の回収数(FM ≤ 0、FM ≤ 2)。in-sample の記述統計として扱う。
  - argmax の acc、誤結合、見逃し。
  - truncated と error の件数。input_tokens の中央値。

## 分解の定義
- 入力+形式の効果(d1): AUC(C2b) - AUC(C1b)。base 同士の AUC(C2a) - AUC(C1a) も併記する。
- モデルの効果(full 入力・同一形式): AUC(C3) - AUC(C2a)。
- C4 が得られたら、モデルの効果(compact 入力)は AUC(C4) - AUC(C1a / C1b)、Jev 側の入力+形式の効果は AUC(C3) - AUC(C4)。

## 判定規則(事前固定)
- **入力・形式が主因**: C2a か C2b の AUC が C3 との差 0.03 以内、かつ FM ≤ 2 の回収数が 30 以上。
- **モデル能力が主因(full 入力の条件で)**: C3 - C2a ≥ 0.05、かつ CI の下限 > 0、かつ C2a と C2b の FM ≤ 2 の回収数がどちらも 25 未満。
- 上のどちらでもなければ **不明瞭**。その場合は C4 と Gold 監査の結果を待つ。
- C2 で truncated が 5% を超えたら、C2 は入力の同一性が崩れたものとして **無効** にする(同じ設定で再実行はしない)。
- seed は 1 つで n=106。結果はパイロットとして読み、採用判断には使わない。

## 固定するもの
- `dev_real.cases.jsonl` の sha256。`p1/p1_result.json` に記録してある。
- d1 の revision: `051bcc464b01b9f92942b364d9586b0ef5912432`。
- la10 のアダプタ: `experiments/lora/mix-la10/adapter`。
- GPU: 5060 Ti。`experiments/.gpu0.lock` で占有する。
- 出力先: `experiments/p0_sameinput/C2a`、`C2b`。
