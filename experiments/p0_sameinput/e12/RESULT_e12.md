# RESULT E12 (2026-10-20) — PREREG_e12.md (sha256 1461c93f…) の判定
すべての run が有効:
- 再現 gate は差 0.0(R-C1b、R-C2b とも既存の結果と完全一致)。
- error 0、truncated 0。
- 出力の hash は `OUTPUT_SHA256SUMS`、詳細は `e12_result.json`。

| AUC (d1 la10) | select | formation |
|---|---|---|
| compact | 0.862 (C1b) | 0.738 (E2) |
| full | 0.853 (E1) | 0.769 (C2b) |

効果(thread cluster bootstrap、95% CI):
- Evidence: select 内 −0.009 [−0.045, +0.023]、formation 内 +0.031 [−0.023, +0.082]
- 判定形式: compact 内 −0.124 [−0.209, −0.051]、full 内 −0.084 [−0.166, −0.020]
- 交互作用: +0.040 [−0.011, +0.092]

**判定: Case B(判定形式への依存)。**
- E2−C1b は「低下」の基準を満たす。
- E1−C1b は「維持」の基準を満たす。

副指標(探索的。事前登録で副指標として宣言済み):
- formation の中でも、target_work の 2 択(W001 / NONE、Atra の文言)の AUC は 0.855(E2)と 0.864(C2b)で、select と同じ水準。
- 失われているのは decision 5 択の P(MERGE)+P(UPDATE) の順位。
- P(MU)/(P(MU)+P(CREATE)) でも AUC は 0.73〜0.74 で、ABSTAIN/IGNORE の質量を除いても回復しない。

低 FM 域(in-sample の記述値):
- TP@FM≤2 は C1b 17、E1 25、E2 16、C2b 15。
- cross-fit の FM≤2 規則では、C1b が FM 6 / FN 26、E1 が FM 4 / FN 27 で、差はない。
