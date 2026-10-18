# autoresearch — d1-3B LoRA の 1 変更ずつの改善ループ（2026-10-18〜）

- **Verification:** `VERIFIED_LOCAL`（2026-10-19、ローカル成果物で確認。実行は別セッション。一部は ledger の値のみ、下記に明記）
- **Model:** LiquidAI/d1-3B（`051bcc4`）
- **Local path:** `experiments/autoresearch`（手順 `program.md`、結果 `results.tsv`）

**目的：** karpathy/autoresearch に倣い、学習コードを 1 か所ずつ変えて 3 seed で学習し、採否を機械的に決める。

**条件：**
- 学習は AWS g6.xlarge で 3 seed を並列実行。評価はローカル GPU で Full Replay（ENSEMBLE_LORA の argmax、閾値なし）。
- 採否の指標 `err`：test2 の Full Replay における 重複＋混在＋余計な必須＋必須見逃し の 3 seed 平均。小さいほど良い。REQUIRED は 2026-10-18 ルーブリックで再ラベルした test2 正解で数える。
- 採用条件：シナリオ×seed の 2 段ブートストラップで P(新 < 最良) ≥ 0.8、かつ誤マージ・完全再現が悪化しないこと。
- dev3 は確認専用（選択には使わない）。封印データには触れない。

**結果：**

| id | err | 差の CI（最良比） | AWS 費用（USD） | 判定 | 変更 |
|---|---:|---|---:|---|---|
| base-trap | 25.0 | — | 0 | 基準 | trap0/1/2（consensus_v2＋train8） |
| base-trap（再ラベル正解） | 25.3 | — | 0 | 基準 | 同上を再ラベル済み正解で再採点 |
| E1-fix9 | 28.3 | −5.0〜+11.3 | 3.57 | 不採用 | consensus_v3＋train9（UNKNOWN の対例）。必須見逃し +2.7、重複 +1.3 |
| E2-la1 | 26.3 | −5.7〜+7.3 | 6.55 | 不採用 | fix9 に LA_TAU=1。P = 0.38、必須見逃し +3.3（CI > 0） |

- base-trap の 25.0 は、`t2/trap{0,1,2}/replay.total.json` から再計算して一致を確認した（24 / 26 / 25）。
- E1・E2 の err と CI は、再ラベル済み正解で採点した `results.tsv` の値である。元の正解での各 seed 値（`t2/fix*`、`t2/la1*`）は存在するが、再ラベル版の再計算はしていない（報告値・未検証）。
- dev3 確認（`results.tsv`、報告値・未検証）：E2-la1 は trap 比で余計な必須 −4.3［−8.7, −0.3］、重複 −1.0（有意差なし）。E1-fix9 は余計な必須 −1.7［−6.0, +2.7］。
- AWS 費用の累計は ledger で 10.58 USD（上限 50 USD）。

**未検証：** E1・E2 の err の再計算、dev3 確認値の照合、3 seed 以外の再現性。2026-10-19 01:50 以降に別セッションの評価（nc-eval）が実行中で、その結果は未記録。

**次の実験：** UNKNOWN 例の追加（ルールでラベルを決める最小対）を、reweight による複製の代わりに用いた学習を 3 seed で評価する（別セッション経由で伝えられた PM 承認の修正指示）。
