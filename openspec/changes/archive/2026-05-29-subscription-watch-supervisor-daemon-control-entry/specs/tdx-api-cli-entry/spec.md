## ADDED Requirements

### Requirement: API CLI SHALL expose explicit supervisor daemon bridge controls

The API CLI bridge command group SHALL expose explicit supervisor daemon status, start, and stop commands that dispatch through the bridge registry client.

#### Scenario: Caller reads supervisor daemon status through CLI

- **WHEN** a caller invokes `tdxquant bridge watch-supervisor-daemon-status`
- **THEN** the CLI MUST require `--registry` and `--worker`
- **AND** it MUST dispatch to the supervisor daemon status registry helper
- **AND** it MUST NOT execute task/report/trade/workflow/catalog steps.

#### Scenario: Caller starts supervisor daemon through CLI

- **WHEN** a caller invokes `tdxquant bridge watch-supervisor-daemon-start`
- **THEN** the CLI MUST require `--registry`, `--worker`, and `--max-ticks`
- **AND** it MUST accept optional `--interval-seconds`, `--loop-sleep-seconds`, `--reason`, and `--owner-token`
- **AND** it MUST dispatch to the supervisor daemon start registry helper without changing default watch lifecycle behavior.

#### Scenario: Caller stops supervisor daemon through CLI

- **WHEN** a caller invokes `tdxquant bridge watch-supervisor-daemon-stop`
- **THEN** the CLI MUST require `--registry`, `--worker`, and `--owner-token`
- **AND** it MUST accept optional `--reason`
- **AND** it MUST dispatch to the supervisor daemon stop registry helper without bypassing controller ownership checks.
