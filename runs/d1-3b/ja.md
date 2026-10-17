# ja — Japanese paraphrase D ablation

- **Verification:** `REPORTED_ONLY`（Agent Handoff、2026-10-17時点。現在のプロセス状態は未確認）
- **Model:** LiquidAI/d1-3B
- **Goal:** s85の日本語質問文への感度を改善し、言い換えD単独の効果を切り分ける。
- **Reported local path:** `experiments/lora/mix-ja`
- **Reported state:** 学習中。完了後にv3が自動開始する設定との報告。
- **Result:** 未取得。完了・改善・失敗を推測しない。

## 作業の制約

- 既存の学習ジョブと子プロセスを確認するまで新規GPUジョブを起動しない。
- 言い換えCは確認用として学習に使用しないという既存の取り決めを維持する。
- 実験が終了したら結果を実測値で追記するか、新しいRun IDで記録する。

