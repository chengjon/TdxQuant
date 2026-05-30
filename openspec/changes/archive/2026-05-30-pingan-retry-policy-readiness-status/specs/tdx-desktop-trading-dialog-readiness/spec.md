## ADDED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose read-only retry policy status

The stable PingAn dialog readiness workflow SHALL expose a read-only `retry_policy_status` object in `desktop_lifecycle_gate_status`.

#### Scenario: Caller checks dialog readiness before retry policy is implemented

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(...)`
- **THEN** `desktop_lifecycle_gate_status.retry_policy_status.status` SHALL be `not_configured`
- **AND** the payload SHALL include `execution_mode=readonly_policy_status`, `retry_executed=false`, `backoff_executed=false`, `recovery_executed=false`, `resubmission_executed=false`, a `policy_source`, and a `configured_policy` object.

#### Scenario: Retry policy status remains read-only

- **WHEN** `retry_policy_status` is returned
- **THEN** the workflow MUST NOT retry lookups or orders, sleep for backoff, recover exception popups, resubmit orders, or write state, ledger, or audit artifacts
- **AND** `desktop_lifecycle_gate_status.side_effect_level` SHALL remain `none`.

## MODIFIED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose lifecycle gate status

The stable PingAn dialog readiness workflow SHALL expose a readonly `desktop_lifecycle_gate_status` payload that summarizes the lifecycle evidence produced by the dialog lookup checks without performing order submission or control dispatch.

#### Scenario: Caller checks lifecycle gate status for both dialogs

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(dialog="both")`
- **THEN** the result data SHALL include `desktop_lifecycle_gate_status`
- **AND** the payload SHALL include confirm dialog lookup status, result dialog lookup status, result confirm-button lookup status, exception popup lookup status, dialog lookup mode, confirm/result timeout settings, declared process/window ownership inputs, passive observed process/window ownership status, read-only retry policy status, `execution_mode=readonly_dialog_readiness`, and `side_effect_level=none`.

#### Scenario: Lifecycle gate status remains partial

- **WHEN** `desktop_lifecycle_gate_status` is returned
- **THEN** the payload SHALL identify the evidence scope as partial desktop lifecycle evidence
- **AND** it SHALL list remaining lifecycle gates for exception popup handling, retry policy, process/window lifecycle ownership, audit evidence, and acceptance evidence.
