## 1. Run Artifact Contract

- [x] 1.1 Add `tdxquant/subscription_watch_run.py` to own `run_id` directories and manifest/status/summary payload builders.
- [x] 1.2 Refactor `TdxTaskManager.subscription_watch(...)` to write canonical run artifacts under a per-run directory while preserving legacy mirrored output paths.
- [x] 1.3 Extend the normalized subscription event row contract with stable `capability`, `run_id`, and fixed `reconnect_metadata` fields.

## 2. Replay Fixtures And Tests

- [x] 2.1 Register `subscription-watch` run artifact fixtures in `tdxquant/replay_fixtures.py` and add representative JSON/JSONL samples under `tdxquant/fixtures/provider/`.
- [x] 2.2 Add or update contract tests for `subscription_watch_run`, subscription event rows, replay fixtures, and task-manager run artifact behavior.
- [x] 2.3 Re-run targeted CLI coverage for `subscription-watch` to confirm the existing stable entrypoint still dispatches correctly.

## 3. Documentation And Validation

- [x] 3.1 Update roadmap and capability documentation to describe the run artifact contract and canonical `events.jsonl` behavior.
- [x] 3.2 Validate the implementation with the targeted pytest suite covering manager, fixture, event-contract, and helper behavior.
- [x] 3.3 Archive the completed change after syncing the delta specs back to the main spec set.
