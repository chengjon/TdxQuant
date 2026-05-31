## ADDED Requirements

### Requirement: PingAn live/manual acceptance recorder SHALL create controlled acceptance artifacts

`TdxTaskManager.pingan_live_manual_acceptance(...)` SHALL create a controlled `tdx.desktop_trade.pingan_live_manual_acceptance.v1` JSON artifact from explicit operator-provided outcomes.

#### Scenario: Recorder writes complete manual acceptance artifact

- **GIVEN** a caller provides output path, operator, environment, and all required outcomes
- **WHEN** `TdxTaskManager.pingan_live_manual_acceptance(...)` runs with `dry_run=false`
- **THEN** it SHALL write a JSON artifact with `schema=tdx.desktop_trade.pingan_live_manual_acceptance.v1`
- **AND** the artifact SHALL include `operator`, `environment`, `accepted_at`, and accepted outcomes for `confirmed`, `rejected`, `failed`, and `exception`
- **AND** the result data SHALL include `live_manual_acceptance_record`
- **AND** the record SHALL expose `artifact_written=true`, `covered_outcomes`, `missing_outcomes`, `execution_mode=manual_acceptance_record`, and `side_effect_level=file_write`.

#### Scenario: Recorder dry-run does not write artifact

- **GIVEN** a caller provides valid manual acceptance inputs
- **WHEN** the task runs with `dry_run=true`
- **THEN** it SHALL return the same artifact payload and metadata
- **AND** it SHALL include `artifact_written=false`
- **AND** it SHALL NOT create or overwrite the output file
- **AND** `side_effect_level` SHALL be `none`.

#### Scenario: Missing required outcomes are rejected

- **GIVEN** a caller omits one or more required outcomes
- **WHEN** the task validates the recorder request
- **THEN** it SHALL return `ErrorCode.INVALID_REQUEST`
- **AND** it SHALL list the missing outcomes
- **AND** it SHALL NOT write the artifact.

#### Scenario: Existing output path is protected by default

- **GIVEN** the output path already exists
- **WHEN** the task runs with `overwrite=false`
- **THEN** it SHALL return `ErrorCode.INVALID_REQUEST`
- **AND** it SHALL NOT overwrite the existing artifact.

