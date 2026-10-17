# Agent rules — Atra-llmLab

## Authority and scope

- Atra-workunitOS owns product UX, the decision contract, validation, WorkStore, source access, and production changes. This lab owns experiments and reproducibility only.
- The PM makes product adoption decisions. Never deploy, merge, edit production Atra code, alter its UX, or write live `slc.json` from a lab experiment.
- Optimize (1) absolute Formation/Personal quality against a matched Jev baseline, then (2) end-to-end cost per correct decision under hard safety/error constraints. Do not claim Jev superiority without matched test conditions.
- Prefer existing project code, Python standard features and existing dependencies. Do not add speculative wrappers, registries, services, dashboards or generalized frameworks. Follow Ponytail and Karpathy: think before coding, make surgical changes, verify goals.

## Before any experiment

- Inspect active GPU/Python jobs and child processes. One GPU job at a time; never restart or kill a running ja/v3 chain without explicit authorization. RTX 4060 may be used only with permission.
- Write a falsifiable prediction, baseline, evaluation dataset/split, success and kill conditions before changing code. Identify model, adapter, LoRA scale, threshold, environment, source-contract SHA, and hashes.
- Protect train/dev/validation/test partitions. Sealed datasets must not be opened, tuned against or re-used. Follow the existing test5 preregistration before any authorized one-time evaluation.
- Do not send private Slack/Gmail/GitHub evidence or credentials to external APIs. Do not publish actual work data, model weights or adapters.
- Inspect all affected callers, fixtures, tests, and failure boundaries before editing. Reuse existing adapters/evaluators where possible.

## Measurement

- Read [docs/measurement.md](docs/measurement.md) before making performance or quality claims.
- Alternate control measurements during performance sweeps; separate startup/warmup, detect CPU fallback, record VRAM, sample size, failures and noise.
- Evaluate both *single judgments* and *Full Replay*; preserve false merges, false DONE, missed REQUIRED, evidence grounding and ABSTAIN/coverage separately.
- Never optimize a synthetic held-out set after viewing its results. Claude-generated labels are not independent human gold.
- Keep failures and rejected hypotheses with their numbers and the exact experiment ID. Don't change or overwrite a finished run; use a new run ID.

## Organization and handoff

- `runs/index.csv` is the searchable experiment registry. One row per completed or in-progress run. Record paths and validity; don't invent results.
- Run notes are `runs/<model>/<run-id>.md`; include Goal, Baseline, Change, Prediction, Results, Decision, Risks and Next Action. For an unverified handoff use `REPORTED_ONLY`.
- Human-facing READMEs/docs may be Japanese; commands, schemas, agent rules and machine-readable fields are English.
- Summarize work as FACT / INFERENCE / UNKNOWN. State not-tested areas and risks explicitly. No push/PR to Atra without PM authorization.

