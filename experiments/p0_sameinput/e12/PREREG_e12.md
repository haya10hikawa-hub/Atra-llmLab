# PREREG E12 — d1 la10 の Pair ranking はどこで崩れるか(Evidence × 判定形式の 2×2)
2026-10-20、GPU 実行の前に書いた。dev_real の pair 106 件(正例 53)のみ。test7 は開封しない。Jev へは送信しない。学習しない。閾値も決めない。

## 1. 仮説
- H_E(Evidence): full view に変えると、select 形式のままでも AUC が下がる。
- H_F(判定形式): Atra の 5 択 Formation に変えると、compact のままでも AUC が下がる。
- H_I(相互作用): 片方ずつの変更では AUC が維持され、両方を変えたときだけ下がる。
- H_D(タスク特化): 片方ずつの変更でも、どちらでも下がる。la10 が compact・select に強く適応している。
- 対立仮説(H0): どの効果も CI で 0 と区別できない。小標本で原因は未確定。

## 2. 監査の結果(実行前に確認したこと、FACT)
d1 の prompt は、固定の system + `render_state(state)`(json_only)+ 質問ごとの suffix でできている(`runner._request`)。
状態は共通の prefix で、質問は独立した branch として採点される。したがって 1 つのセルは「(state, questions)」の組で完全に決まる。

| 要素 | C1b(compact・select) | C2b(full・formation) | 2×2 での扱い |
|---|---|---|---|
| system prompt | d1 の DEFAULT_SYSTEM | 同じ | 固定 |
| state | `select_input` の compact state | `case.view` | **Evidence 因子** |
| evidence | 最後の 3 件 × 200 字、signal item は 600 字、attrs は 5 種のみ、`continues_thread` と `owns_this_signal_thread` の真偽値を付ける | 全件・全文・全 attrs、`member_refs`、`thread_key`、`signal_id`、`link_hints` | Evidence 因子(量と構造が一体) |
| 質問 | PARA の same_work 変種 0 の指示 + "Pick the one..."。選択肢は {NONE, W001: title} | Atra の decision 5 択(CREATE/MERGE/UPDATE/IGNORE/ABSTAIN)+ target_work(W001: title と状態) | **判定形式因子**(文言・選択肢数・ABSTAIN/IGNORE の有無が一体) |
| score | P(select=W001) | P(MERGE)+P(UPDATE) | 判定形式に従う |
| モデル・アダプタ・scale | d1 rev 051bcc46、la10(r=16, alpha=32)を merge | 同じ | 固定 |
| CLI | `pairwise.py`(PAIRWISE_SELECT) | `infer.py` | 本実験では両方とも `run_cell.py`(既存関数をそのまま再利用) |
| data / gold / fold | dev_real、folds.json | 同じ | 固定 |
| truncation | 0 | 0 | 毎回記録する |

compact で実際に本文が失われる pair は 52/106 ある(evidence が 3 件超: 9、本文 200 字超: 46、signal item 600 字超: 10)。state の JSON 文字数の中央値は compact 1092 / full 1684。

## 3. 固定する hash(sha256)
- dev_real.cases.jsonl: 7e7b96ad785be0db726ad56fdd85d2f1e1659ab643b43b5f80908119186aee5f
- folds.json: a64fe1d70c3be54271959316410faf7ce88d8cc2243b8974ed010ce4517e1b79
- PARA.questions.json: 3a47da083cab862ea6c6196d00eb8a72fd106dd0423d17f14447cd54726f9adf
- infer.py: 748d0d35763b124c5eb1ee1ee936185ca6ae5716bf02867b59448353774e7286
- pairwise.py: eadc51b7889e2b97ce0cb93cbae96f7e00b7127f6aab2bebaa7fe3953da1b351
- la10 adapter_model.safetensors: 8e0f2b5d35ed2c10afbd4db41a321472586c55947918bd614a61b7ab1df863e1
- la10 adapter_config.json: fb4a09e9be80830a1e828358bed9542e9b8ec4e84ac1abf54482a7fe050ccaa2
- d1 model.safetensors: 50e03317847caf6df9a9aee27ed40f20554a86a21e60d1d47ba41a422b546c0c
- d1 prompt.py: a20b5f52e41a6d29e694bb8c861a5a4803ce3eb69364edad79511ccf8edb5c31
- d1 runner.py: 24d3ae718e9f9717771c0df39c93d324d00aa27bf3e12bab085c0922096cb0dd
- run_cell.py: c129815d14f142962cedd571c05f2805ea5ad4bca691a9b43b90d5c0e3cf29e1
- run_e12.sh: da78958b5682f865d782a61572ff8bb19cf76607550fe861ea57d23d1a9fda4e
- score_e12.py: 2fcde195dea447c792b961f1bbee3e8f06a6fbaad65704a814d1a7ec6f09b5dc

## 4. セル(すべて d1 + la10、`run_cell.py <state> <questions>`)
| セル | state | 質問 | score |
|---|---|---|---|
| R-C1b | compact | select | P(W001)。既存の C1b の再現確認を兼ねる |
| E1 | full(`case.view`) | select(C1b と同じ質問の object) | P(W001) |
| E2 | compact(C1b と同じ state の object) | formation(`case.questions`) | P(MERGE)+P(UPDATE) |
| R-C2b | full | formation | P(MERGE)+P(UPDATE)。既存の C2b の再現確認を兼ねる |

argmax の規則:
- select は P(W001) > P(NONE)。
- formation は、decision の argmax が MERGE か UPDATE で、かつ target の P(W001) > P(NONE)。

## 5. 指標
各セルについて次を計算する。
- pair AUC(全体、fold A、fold B)。
- FM≤0 / FM≤2 / FM≤5 での正例回収数。in-sample の閾値掃引による探索用の値。
- argmax の acc、FM、FN。
- 正例と負例の score 分位点。
- fold をまたぐ cross-fit 閾値(acc 最大の規則、FM≤2 の規則)での FM と FN。cross-fit では FM≤2 は保証されない。
- p50 / p95 遅延、truncated の件数、error の件数。

副指標(formation のみ。score の意味が select と同じかを確かめるため):
- P(MU)/(P(MU)+P(CREATE)) の AUC。
- P(target=W001) の AUC。
- ABSTAIN と IGNORE の質量の平均。

## 6. Bootstrap
- new_signal の thread_key をクラスタとした、全セル対応の cluster bootstrap。75 クラスタ、2000 回、seed 0。
- 同じ resample から、次の差の 95% パーセンタイル CI を計算する: E1−C1b、C2b−E2、E2−C1b、C2b−E1、交互作用(C2b−E2−E1+C1b)。

## 7. 判定規則(固定)
用語の定義:
- **低下**: 点推定 ≤ −0.03、かつ CI の上限 < 0。
- **維持**: 点推定 > −0.03。

判定:
- Case A: E1−C1b が低下、E2−C1b が維持 → Evidence が原因候補。
- Case B: E2−C1b が低下、E1−C1b が維持 → 判定形式への依存が原因候補。
- Case C: 両方とも維持、かつ交互作用の CI の上限 < 0 → 入力 × 判定形式の相互作用が原因候補。
- Case D: 両方とも低下 → la10 の compact・select への特化が疑われる。
- Case E: 上のどれにも当たらない → 未確定。

低 FM 域(TP@FM≤2)は記述的に報告するだけで、判定には使わない。

## 8. 無効 run
- **再現 gate**: R-C1b と R-C2b の score が既存の結果と最大で 0.01 を超えて違ったら、実装が等価でないとみなし、E1 と E2 を含む全セルを INVALID にする(削除しない)。
- error が 1 件以上、または truncated が 5% を超えたセルは INVALID にする。再実行は 1 回まで許し、そのことを記録する。
- GPU lock が占有されていたら実行しない。

## 9. 残る交絡(この設計では分離しない)
- 判定形式の因子には、指示文の文言、選択肢の数(2 か 5)、ABSTAIN/IGNORE という「逃げ先」の有無、target の基準文(title だけか、状態を含むか)が混ざっている。
- Evidence の因子には、本文量の違いと構造の違い(フィールド名、真偽値の手がかり、attrs、member_refs)が混ざっている。
- seed は 1 つ、アダプタも 1 つ(la10)。base の d1 で同じ 2×2 は行わない。

## 10. 過適合のリスク
- dev_real は P0 と P1 で既に何度も見ている。本実験では選択も調整もせず、診断だけに使う。
- ここで得た「良い条件」を採用の根拠にはしない。採用の判断には、別の未使用データか、凍結後の test7 が要る。
