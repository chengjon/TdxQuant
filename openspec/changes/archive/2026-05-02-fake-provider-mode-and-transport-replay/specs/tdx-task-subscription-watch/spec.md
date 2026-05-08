## ADDED Requirements

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
