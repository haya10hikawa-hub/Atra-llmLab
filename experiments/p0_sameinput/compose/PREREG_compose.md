# PREREG compose — 2択の連鎖は、5択の直接判定より正確か(既存出力の再採点のみ)
2026-10-20、計算の実行前に書いた。dev_real の全 157 件(pair 106、signal 51)。推論・学習・外部送信はしない。test7 は開封しない。

## 問い
2択の判断を組み合わせたもの(is_work → 同一 Work か)は、5択(CREATE/MERGE/UPDATE/IGNORE/ABSTAIN)を直接判定するより正確か。

## Gold で評価できる範囲(制約)
- dev_real の Gold は、pair では same / not_same、signal では work / not_work だけ。
- MERGE と UPDATE の区別、および ABSTAIN の妥当性は、**Gold がないため評価できない(UNKNOWN)**。
- したがって、ここでの「正確さ」は「結合すべきものを結合し、仕事を仕事と判定する」という最終判断の正確さを指す。

## アーム(既存の出力のみ)
| アーム | 出力元 | pair の score | signal の score | argmax |
|---|---|---|---|---|
| d1_chain | la10 compact の probs(C1b) | is_work × P(select=W001) | is_work | is_work ≥ .5、かつ P(W001) > P(NONE) |
| d1_direct5 | la10 full 5 択(C2b) | P(MERGE)+P(UPDATE) | 1−P(IGNORE) | decision の argmax が M/U、かつ P(target W001) > .5 |
| jev_chain | Jev の同じ 1 回の呼び出し | (1−P(IGNORE)) × P(target=W001) | 1−P(IGNORE) | P(IGNORE) < .5、かつ P(target) > .5 |
| jev_direct5 | Jev(C3) | P(MERGE)+P(UPDATE) | 1−P(IGNORE) | 既存の argmax(choice) |

補助として、pair だけで evidence を固定した比較も行う: d1 compact の P(select)(C1b)と、d1 compact の 5 択 P(MU)(E2)の AUC。

## 指標
- 主指標: cross-fit の accuracy(全 157 件)。閾値は種類別(pair / signal)に、反対側の fold で acc 最大になるよう決める。
- 副指標: pair AUC、signal AUC、argmax の accuracy、FM(signal では FP)、FN。
- 差の CI: new_signal の thread_key をクラスタとした対応 cluster bootstrap。2000 回、seed 0、95% パーセンタイル。

## 判定規則
- **連鎖が優れる**: cross-fit acc の差の CI の下限 > 0、かつ pair の FM が直接判定より +2 を超えて増えない。
- **連鎖が劣る**: CI の上限 < 0。
- 上のどちらでもなければ **不明瞭**。
- 主判定は d1 の d1_chain − d1_direct5。Jev 内の比較は参考にとどめる。

## 交絡
- d1_chain は compact、d1_direct5 は full。E12 では Evidence の効果は 0 と区別できなかったが、ゼロとは確定していない。補助の compact 比較で確かめる。
- jev_chain は、5 択の呼び出しの中から 2 択の要素を取り出したもので、独立した 2 択の呼び出しではない。
- seed は 1 つ。dev_real は 5 回目の診断利用。結果は採用判断に使わない。

## hash(sha256)
- compose.py: 4f2aecbd01b1a92da70a1eec44c2a557a8e8b2211c22d3cc1521d3336739f17e
- la10 probs: f9b066c9491629a25bbceedd1ee6425a765af7cd25bd0bbae9d5d51928308cb2
- C2b answers: bb5d066bb5f63e5b60b5b7ee329c9f7d32a2a779cb2797555282004369b09fab
- Jev answers: 0d1ac7583f8ce5296c17503f6a6247298c79fd310e0486f7eb1b7a85a4f77196
- E2 out: c5e2377aba4421b54fceaef976199f32a4c7c6ad24090ad25f4999f8c90815af
- dev_real / folds: PREREG_e12.md と同じ
