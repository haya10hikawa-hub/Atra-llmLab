# P0 partial result (2026-10-20) — C4 (Jev compact) is pending, so this is not the final decomposition
Scorer: `score_p0.py` → `p0_result.json`. Hashes: `SHA256SUMS`. dev_real pair n=106 (positives 53). Single seed. truncated = 0 and errors = 0 in every cell.

| cell | condition | pair AUC | TP@FM≤2 | argmax acc / FM / miss |
|---|---|---|---|---|
| C1a | d1 base, compact select | 0.687 | 10 | 0.585 / 3 / 41 |
| C1b | d1 la10, compact select | 0.862 | 17 | 0.604 / 2 / 40 |
| C2a | d1 base, full 5-way | 0.758 | 11 | 0.585 / 8 / 36 |
| C2b | d1 la10, full 5-way | 0.769 | 15 | 0.604 / 0 / 42 |
| C3 | Jev, full 5-way | 0.904 | 35 | 0.783 / 5 / 18 |

Differences (cluster bootstrap 95% CI):
- C3−C2a +0.146 [+0.069, +0.249]
- C3−C2b +0.136 [+0.051, +0.239]
- C2b−C1b −0.094 [−0.178, −0.026]
- C2a−C1a +0.071 [−0.021, +0.166]

Verdict under the preregistered rules: **model capability is the main cause, under the full-input / same-format condition.**
- C3−C2a ≥ 0.05, CI lower bound > 0, and C2a and C2b TP@FM≤2 are 11 and 15 (both < 25).
- Holding input and format equal to Jev's does not close the gap.

Limits:
- The verdict covers the full 5-way format only.
- d1's best condition is la10 compact select (0.862). The gap that matters for release, C3 versus C1b, is still confounded by input and format until C4 exists.
- Format and input are not separated from each other within a cell.
- Gold audit is pending, so labels could still move every number above.
