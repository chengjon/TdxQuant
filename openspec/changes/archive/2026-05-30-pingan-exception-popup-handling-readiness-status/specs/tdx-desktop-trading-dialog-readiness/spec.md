## ADDED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose read-only exception popup handling status

The stable PingAn dialog readiness workflow SHALL expose a read-only `exception_popup_handling_status` object in `desktop_lifecycle_gate_status`.

#### Scenario: Caller checks dialog readiness with an exception-like popup detected

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(...)`
- **AND** `exception_popup_lookup.detail.exception_detected` is true
- **THEN** `desktop_lifecycle_gate_status.exception_popup_handling_status.status` SHALL be `manual_required`
- **AND** the payload SHALL include `handling_available=false`, `execution_mode=readonly_handling_status`, lookup status, matched keywords, and false execution flags for close, confirm click, recovery, retry, and resubmission.

#### Scenario: Exception popup handling status remains read-only

- **WHEN** `exception_popup_handling_status` is returned
- **THEN** the workflow MUST NOT close the popup, click confirmation controls, retry, recover, resubmit, or write state, ledger, or audit artifacts
- **AND** `desktop_lifecycle_gate_status.side_effect_level` SHALL remain `none`.

## MODIFIED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose lifecycle gate status

The stable PingAn dialog readiness workflow SHALL expose a readonly `desktop_lifecycle_gate_status` payload that summarizes the lifecycle evidence produced by the dialog lookup checks without performing order submission or control dispatch.

#### Scenario: Caller checks lifecycle gate status for both dialogs

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(dialog="both")`
- **THEN** the result data SHALL include `desktop_lifecycle_gate_status`
- **AND** the payload SHALL include confirm dialog lookup status, result dialog lookup status, result confirm-button lookup status, exception popup lookup status, dialog lookup mode, confirm/result timeout settings, declared process/window ownership inputs, passive observed process/window ownership status, read-only retry policy status, read-only exception popup handling status, `execution_mode=readonly_dialog_readiness`, and `side_effect_level=none`.

#### Scenario: Lifecycle gate status remains partial

- **WHEN** `desktop_lifecycle_gate_status` is returned
- **THEN** the payload SHALL identify the evidence scope as partial desktop lifecycle evidence
- **AND** it SHALL list remaining lifecycle gates for exception popup handling, retry policy, process/window lifecycle ownership, audit evidence, and acceptance evidence.
