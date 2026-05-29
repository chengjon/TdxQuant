## ADDED Requirements

### Requirement: Command catalog SHALL expose PingAn trade health readiness entry
The command catalog SHALL expose a PingAn trade health readiness entry for discovery and non-executing planning while reusing the existing read-only `trade health` workflow.

#### Scenario: Caller lists the health readiness entry
- **WHEN** a caller lists catalog entries with a `health` label
- **THEN** the catalog MUST include `trade-health-pingan-readiness`
- **AND** the entry MUST resolve to a trade preset whose command is `health`

#### Scenario: Caller plans the health readiness entry
- **WHEN** a caller plans `trade-health-pingan-readiness`
- **THEN** the plan summary MUST include trade input boundary metadata for the `health` command
- **AND** the boundary MUST identify the workflow as read-only desktop health readiness input coverage
- **AND** planning MUST NOT execute the trade health workflow

