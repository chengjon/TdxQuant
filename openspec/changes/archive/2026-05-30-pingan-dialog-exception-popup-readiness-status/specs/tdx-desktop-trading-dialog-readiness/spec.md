## ADDED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose passive exception popup lookup evidence

The stable PingAn dialog readiness workflow SHALL expose a passive `exception_popup_lookup` check when result dialog readiness is requested.

#### Scenario: Caller checks result dialog readiness with an exception-like popup visible

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(...)` for `dialog=result` or `dialog=both`
- **AND** the current result dialog text contains exception-like evidence
- **THEN** the result data SHALL include an `exception_popup_lookup` check
- **AND** the check detail SHALL include whether an exception popup was detected, matched keywords, and the passive dialog text payload.

#### Scenario: Exception popup lookup remains read-only

- **WHEN** `exception_popup_lookup` is returned
- **THEN** the workflow MUST NOT close the popup, click confirmation controls, submit orders, write trade state, write audit artifacts, or mutate the submission ledger
- **AND** `desktop_lifecycle_gate_status.side_effect_level` SHALL remain `none`.

## MODIFIED Requirements

### Requirement: Stable desktop trading dialog readiness SHALL expose lifecycle gate status

The stable PingAn dialog readiness workflow SHALL expose a readonly `desktop_lifecycle_gate_status` payload that summarizes the lifecycle evidence produced by the dialog lookup checks without performing order submission or control dispatch.

#### Scenario: Caller checks lifecycle gate status for both dialogs

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(dialog="both")`
- **THEN** the result data SHALL include `desktop_lifecycle_gate_status`
- **AND** the payload SHALL include confirm dialog lookup status, result dialog lookup status, result confirm-button lookup status, exception popup lookup status, dialog lookup mode, confirm/result timeout settings, declared process/window ownership inputs, `execution_mode=readonly_dialog_readiness`, and `side_effect_level=none`.

#### Scenario: Lifecycle gate status remains partial

- **WHEN** `desktop_lifecycle_gate_status` is returned
- **THEN** the payload SHALL identify the evidence scope as partial desktop lifecycle evidence
- **AND** it SHALL list remaining lifecycle gates for exception popup handling, retry policy, process/window lifecycle ownership, audit evidence, and acceptance evidence.

