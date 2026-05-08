## MODIFIED Requirements

### Requirement: Subscription watch task SHALL support replay-mode run artifact materialization
The system SHALL let `subscription-watch` run in replay mode by materializing a completed run artifact bundle from fixture-backed event data instead of opening a live runtime subscription session.

#### Scenario: Replay-mode subscription watch materializes a completed run from built-in fixtures
- **WHEN** a caller invokes `subscription-watch` in replay mode without explicitly overriding the fixture source
- **THEN** the task MUST create a fresh `run_id` directory and write canonical `events.jsonl`, `status.json`, `summary.json`, and `manifest.json` artifacts from the built-in replay bundle
- **AND** the returned task result MUST report a completed replay run without opening a live runtime subscription session

#### Scenario: Replay-mode subscription watch uses an explicit replay artifact source
- **WHEN** a caller invokes `subscription-watch` in replay mode with an explicit replay manifest path or replay run directory
- **THEN** the task MUST materialize a fresh completed run from that replay source
- **AND** the task MUST rewrite run identity and artifact paths for the new materialized run instead of reusing the original source paths verbatim

#### Scenario: Replay-mode subscription watch returns canonical and legacy artifact aliases
- **WHEN** a replay-mode `subscription-watch` task completes successfully
- **THEN** the returned task result MUST expose canonical artifact paths for the new run including `run_dir`, `manifest_path`, `status_path`, `summary_path`, `events_jsonl_path`, and `events_csv_path`
- **AND** the returned task result MUST also preserve the compatibility aliases `jsonl_output_path`, `csv_output_path`, and `status_output_path`

#### Scenario: Replay-mode subscription watch rejects malformed replay input without opening live session
- **WHEN** a caller invokes `subscription-watch` in replay mode with an incomplete or malformed replay source bundle
- **THEN** the task MUST return a stable failed task result with `INVALID_REQUEST`
- **AND** the failed result MUST include replay source metadata for `subscription.watch`
- **AND** the task MUST NOT open a live runtime subscription session
