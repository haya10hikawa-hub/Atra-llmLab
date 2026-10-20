# RESULT compose (2026-10-20) — PREREG_compose.md の判定: **不明瞭**
主判定(cross-fit acc、全 157 件): d1_chain − d1_direct5 = −0.006 [−0.081, +0.070]。

| アーム | pair AUC | signal AUC | cross-fit acc(全体 / pair / signal) | cross-fit の pair FM / FN | argmax acc(全体) |
|---|---|---|---|---|---|
| d1_chain | 0.828 | 0.779 | 0.694 / 0.755 / 0.569 | 13 / 13 | 0.637 |
| d1_direct5 | 0.769 | 0.843 | 0.701 / 0.717 / 0.667 | 11 / 19 | 0.599 |
| jev_chain | 0.905 | 0.708 | 0.758 / 0.802 / 0.667 | 4 / 17 | 0.745 |
| jev_direct5 | 0.904 | 0.708 | 0.720 / 0.745 / 0.667 | 15 / 12 | 0.739 |

- **pair だけ・evidence を固定(compact)した場合**: P(select) 0.862 対 5 択 P(MU) 0.738。差 +0.125 [+0.049, +0.210]。同一性の判断は、2 択の方が明確に優れる。
- **全体で差が出ない理由**:
  - 連鎖では、pair score に is_work を掛けると pair AUC が 0.862 から 0.828 に落ちる。
  - signal では、compact の is_work が 5 択の 1−P(IGNORE) に劣る(AUC 0.779 対 0.843、cross-fit acc 0.569 対 0.667)。
  - pair での利得と signal での損失が相殺している。
- **Jev**: 1 回の呼び出しの中で 2 択要素を組み合わせても、AUC は同じ(+0.001)。acc は +0.038 [−0.007, +0.090] で不明瞭。
- signal の cross-fit acc 0.667 は、一部のアームで「全件を not_work と判定する」自明な解に近い(Jev は FN 16/16)。n=51 の signal の結果は弱い証拠としてしか読めない。
- MERGE と UPDATE の区別、ABSTAIN の妥当性は Gold がないため評価できない(UNKNOWN)。
