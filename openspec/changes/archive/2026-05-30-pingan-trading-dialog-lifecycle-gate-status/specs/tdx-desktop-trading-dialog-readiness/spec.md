## ADDED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose lifecycle gate status

The stable PingAn dialog readiness workflow SHALL expose a readonly `desktop_lifecycle_gate_status` payload that summarizes the lifecycle evidence produced by the dialog lookup checks without performing order submission or control dispatch.

#### Scenario: Caller checks lifecycle gate status for both dialogs

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(dialog="both")`
- **THEN** the result data SHALL include `desktop_lifecycle_gate_status`
- **AND** the payload SHALL include confirm dialog lookup status, result dialog lookup status, result confirm-button lookup status, dialog lookup mode, confirm/result timeout settings, declared process/window ownership inputs, `execution_mode=readonly_dialog_readiness`, and `side_effect_level=none`.

#### Scenario: Lifecycle gate status remains partial

- **WHEN** `desktop_lifecycle_gate_status` is returned
- **THEN** the payload SHALL identify the evidence scope as partial desktop lifecycle evidence
- **AND** it SHALL list remaining lifecycle gates for exception popup handling, retry policy, process/window lifecycle ownership, audit evidence, and acceptance evidence.
## MODIFIED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL remain non-side-effecting

The system SHALL keep the stable dialog readiness workflow read-only. Dialog readiness and its lifecycle gate status SHALL NOT submit orders, confirm pending orders, close result dialogs, write trade state, write audit artifacts, or mutate the submission ledger.

#### Scenario: Caller executes dialog readiness

- **WHEN** a caller executes the stable dialog readiness workflow
- **THEN** the workflow MUST NOT submit or confirm an order
- **AND** it MUST NOT write trade state, audit artifacts, or submission ledger rows
- **AND** `desktop_lifecycle_gate_status.side_effect_level` SHALL be `none`.
