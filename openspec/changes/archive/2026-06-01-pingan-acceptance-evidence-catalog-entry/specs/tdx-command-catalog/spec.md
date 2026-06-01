## ADDED Requirements

### Requirement: Command catalog SHALL register PingAn trade acceptance evidence entry

The command catalog SHALL expose the PingAn trade execution acceptance evidence summary as a discoverable, non-executing trade entry.

#### Scenario: Catalog list discovers acceptance evidence entry

- **WHEN** a caller lists catalog entries with an acceptance or readonly label
- **THEN** the catalog MUST include `trade-acceptance-evidence`
- **AND** the entry MUST identify a trade preset for the `acceptance-evidence` command.

#### Scenario: Catalog plan summarizes acceptance evidence without dispatch

- **WHEN** a caller plans `trade-acceptance-evidence` in summary view
- **THEN** the plan MUST resolve the `acceptance-evidence` trade command
- **AND** it MUST report non-executing catalog planning with `dispatch_executed=false`
- **AND** it MUST NOT execute trade, broker, desktop, task, report, bundle, or status-transition workflows.
