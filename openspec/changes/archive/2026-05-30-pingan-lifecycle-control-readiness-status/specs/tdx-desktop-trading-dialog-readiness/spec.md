## ADDED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose read-only lifecycle control status

The stable PingAn dialog readiness workflow SHALL expose a read-only `lifecycle_control_status` object in `desktop_lifecycle_gate_status`.

#### Scenario: Caller checks dialog readiness without lifecycle control ownership

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(...)`
- **THEN** `desktop_lifecycle_gate_status.lifecycle_control_status.status` SHALL be `not_owned`
- **AND** the payload SHALL include `execution_mode=readonly_lifecycle_control_status`, `control_available=false`, declared `title_keyword` and `exe_path`, and false action flags for start, stop, restart, supervisor ownership, backoff, process kill, and PID ownership.

#### Scenario: Lifecycle control status remains read-only

- **WHEN** `lifecycle_control_status` is returned
- **THEN** the workflow MUST NOT start, stop, restart, kill, supervise, back off, claim PID ownership, write owner tokens, write state, append ledger entries, write audit artifacts, or submit orders
- **AND** `desktop_lifecycle_gate_status.side_effect_level` SHALL remain `none`.

## MODIFIED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose lifecycle gate status

The stable PingAn dialog readiness workflow SHALL expose a readonly `desktop_lifecycle_gate_status` payload that summarizes the lifecycle evidence produced by the dialog lookup checks without performing order submission or control dispatch.

#### Scenario: Caller checks lifecycle gate status for both dialogs

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(dialog="both")`
- **THEN** the result data SHALL include `desktop_lifecycle_gate_status`
- **AND** the payload SHALL include confirm dialog lookup status, result dialog lookup status, result confirm-button lookup status, exception popup lookup status, dialog lookup mode, confirm/result timeout settings, declared process/window ownership inputs, passive observed process/window ownership status, read-only retry policy status, read-only exception popup handling status, read-only statefile lock status, read-only lifecycle control status, `execution_mode=readonly_dialog_readiness`, and `side_effect_level=none`.

#### Scenario: Lifecycle gate status remains partial

- **WHEN** `desktop_lifecycle_gate_status` is returned
- **THEN** the payload SHALL identify the evidence scope as partial desktop lifecycle evidence
- **AND** it SHALL list remaining lifecycle gates for exception popup handling, retry policy, process/window lifecycle ownership, audit evidence, and acceptance evidence.
