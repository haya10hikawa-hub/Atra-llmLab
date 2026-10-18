# trap0 / ens-cons0-seldq0 — d1-3B 誤り分解・リンク罠データ・ensemble と封印 test6 最終評価（2026-10-18）

- **Verification:** `VERIFIED_LOCAL`（ローカル実測。test6 は封印 sN、事前登録 `experiments/PREREG_test6.md` に従い 1 回だけ評価）
- **Model:** LiquidAI/d1-3B（base revision `051bcc46…`）、LoRA r16 / alpha 32、select formulation
- **Arms（test6 で比較）:**
  - R = Jev-preview（API）
  - S = `trap0`：consensus_v2 再ラベル＋全学習プール＋**train8（リンク罠 24 シナリオ）**、argmax・閾値なし。Adapter sha256 `e2de5164aa54ba58…`
  - C = `cons0`＋`seldq0` の 2 モデル ensemble（select 分布の平均、argmax・閾値なし）。Adapter `334e4269421c1ce9…` ＋ `acf5544020126547…`
- **データ:** すべて Claude 生成の合成データ（人間 Gold ではない）。

## 経緯（dev3 で判断。dev3 = 48 シナリオの新規凍結 dev）

1. **test2 での改善は dev3 で再現せず。** test2（24 シナリオ）で選んだ seldq1（0.898）は dev3 で 0.70。小さい dev での選択過適合。
2. **誤り分解（`experiments/dissect/`）:** d1 の単独判断の差は小さい（system acc：Jev 0.932、seldq1 0.880）。誤りの多くは推論能力ではなく、
   - 学習分布の偏り：リンク先が同じ Work である割合が train 90%（75/83）vs dev3 49%（19/39）→「リンクがあれば統合」のショートカット（CUE-TRAP）。
   - test2 で fit した LTT 閾値：dev3 では逆効果（cons0 0.880 → argmax 0.929）。
   - ラベル定義（MERGE/UPDATE、IGNORE）は Jev も同様に外す。
3. **入力アブレーション（推論のみ）:** 全文入力は改善なし（入力切り詰めは原因ではない）。リンク hint 除去で CUE-TRAP 8→0 だが LOOKUP split 3→10（hint を単純スイッチとして使用）。
4. **対策 train8:** 別エージェントで 24 シナリオを作成（cross-link 55 本中 29 本が別 Work）。trap0/trap1（seed 2 本）で CUE-TRAP 0/1、single acc 0.904/0.904。seed のばらつきを超える改善。
5. **ensemble:** 既存 LoRA 7 個の誤りは補完的（any-correct oracle 0.97）。多数決は効かず、確率平均が有効。dev3 の半分で選び残り半分で評価する selection-honest CV（20 分割）で held-out 0.937 vs Jev 0.932。

dev3 Full Replay（argmax・閾値なし）：

| arm | exact | dup | FM | mixed | missed REQ | spurious REQ |
|---|---|---|---|---|---|---|
| Jev-preview | 0.821 | 6 | 12 | 11 | 9 | 3 |
| trap0 | 0.827 | 9 | 9 | 9 | 2 | 11 |
| trap1 | 0.810 | 14 | 10 | 10 | 13 | 9 |
| cons0+seldq0 | 0.799 | 15 | 11 | 11 | 3 | 11 |

## 封印 test6 の結果（1 回のみ、Full Replay、gold Works 92 / gold REQUIRED 25）

括弧内は Jev-preview との差と、シナリオ単位 bootstrap の 90% CI。

| arm | exact | dup | FM | mixed | missed REQ | spurious REQ |
|---|---|---|---|---|---|---|
| R Jev-preview | 0.826 | 3 | 5 | 4 | 8 | 1 |
| S trap0 | 0.870（+4, −4..+13） | 7（+4, 0..+8） | 1（−4, −7..−1） | 1（−3, −6..−1） | 5（−3, −7..0） | 6（+5, +1..+10） |
| C cons0+seldq0 | **0.924（+9, +1..+18）** | 5（+2, −1..+5） | **0（−5, −8..−2）** | **0（−4, −7..−1）** | **4（−4, −8..−1）** | 4（+3, −1..+7） |

単独判断：R acc 0.830 / FM 2 / p95 219 ms（API）、S acc 0.879 / FM 1 / p95 347 ms（ローカル 5060 Ti）。
Personal 単独判断（test6 のラベルは 2026-10-18 ルーブリック以前のため参考）：R verdict 0.761・False DONE 7・REQUIRED precision 0.94、S 0.750・5・0.67。

**判断：** Formation は d1（S・C とも）が Jev-preview と同等以上。C は exact・FM・mixed・missed REQUIRED で有意に上回る。d1 arm 同士の順位（dev3 では S > C、test6 では C > S）はこのデータ規模では安定しない。

**残課題：**
- duplicated（S 7、C 5、Jev 3）と spurious REQUIRED（S 6）。KPI A2（dup ≤ 3）未達。
- 全データが Claude 生成。実データ・人間 Gold では未評価。test6 は消費済みで、次の最終判定には新しい封印データか実データ smoke が必要。
- C は推論 2 回分（latency 約 2 倍）。
- 次の作業：設計書 `reports/design-training-loop-aws-2026-10-18.md`（3 seed 判定、リンク反実仮想 minimal pair、学習高速化、AWS g6.xlarge での並行学習）。

**根拠（lab 内パス）:** `experiments/PREREG_test6.md`、`experiments/test6/*/replay.total.json`、`experiments/dev3/*/replay.total.json`、`experiments/dissect/`、`experiments/ensemble/select_cv.py`、`experiments/consensus/run_trap.sh`。
