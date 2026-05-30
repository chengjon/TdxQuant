# tdx-desktop-trading-dialog-readiness Specification

## Purpose
TBD - created by archiving change add-trade-dialog-readiness. Update Purpose after archive.
## Requirements
### Requirement: Stable desktop trading SHALL expose a read-only dialog readiness workflow
The system SHALL expose a stable non-side-effecting workflow that checks whether the current confirm/result dialogs can be located through the stable desktop trade lookup path.

#### Scenario: Caller checks confirm dialog readiness
- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(...)` for the confirm dialog
- **THEN** the result MUST include a structured readiness summary for the requested dialog target

#### Scenario: Caller checks result dialog readiness
- **WHEN** a caller executes the stable dialog readiness workflow for the result dialog
- **THEN** the summary MUST include the result-dialog lookup outcome and the result confirm-button lookup outcome

### Requirement: Stable desktop trading dialog readiness SHALL support passive and required visibility semantics
The system SHALL let callers choose whether currently absent dialogs are treated as warnings or failures.

#### Scenario: Caller observes dialog readiness without requiring visibility
- **WHEN** a caller executes the stable dialog readiness workflow without `require_visible`
- **THEN** an absent requested dialog MUST be reported as a warning-style readiness outcome

#### Scenario: Caller requires current dialog visibility
- **WHEN** a caller executes the stable dialog readiness workflow with `require_visible`
- **THEN** an absent requested dialog MUST be reported as a failed-style readiness outcome

### Requirement: Stable desktop trading dialog readiness SHALL remain non-side-effecting

The system SHALL keep the stable dialog readiness workflow read-only. Dialog readiness and its lifecycle gate status SHALL NOT submit orders, confirm pending orders, close result dialogs, write trade state, write audit artifacts, or mutate the submission ledger.

#### Scenario: Caller executes dialog readiness

- **WHEN** a caller executes the stable dialog readiness workflow
- **THEN** the workflow MUST NOT submit or confirm an order
- **AND** it MUST NOT write trade state, audit artifacts, or submission ledger rows
- **AND** `desktop_lifecycle_gate_status.side_effect_level` SHALL be `none`.

### Requirement: Stable desktop trading dialog readiness SHALL expose lifecycle gate status

The stable PingAn dialog readiness workflow SHALL expose a readonly `desktop_lifecycle_gate_status` payload that summarizes the lifecycle evidence produced by the dialog lookup checks without performing order submission or control dispatch.

#### Scenario: Caller checks lifecycle gate status for both dialogs

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(dialog="both")`
- **THEN** the result data SHALL include `desktop_lifecycle_gate_status`
- **AND** the payload SHALL include confirm dialog lookup status, result dialog lookup status, result confirm-button lookup status, exception popup lookup status, dialog lookup mode, confirm/result timeout settings, declared process/window ownership inputs, passive observed process/window ownership status, read-only retry policy status, read-only exception popup handling status, read-only statefile lock status, `execution_mode=readonly_dialog_readiness`, and `side_effect_level=none`.

#### Scenario: Lifecycle gate status remains partial

- **WHEN** `desktop_lifecycle_gate_status` is returned
- **THEN** the payload SHALL identify the evidence scope as partial desktop lifecycle evidence
- **AND** it SHALL list remaining lifecycle gates for exception popup handling, retry policy, process/window lifecycle ownership, audit evidence, and acceptance evidence.

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

### Requirement: Stable desktop trading dialog readiness SHALL expose passive process/window ownership observation

The stable PingAn dialog readiness workflow SHALL expose a passive `observed_process_window_ownership` status in `desktop_lifecycle_gate_status`.

#### Scenario: Caller checks dialog readiness with runtime and window observed

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(...)`
- **AND** PingAn runtime/window health discovery succeeds
- **THEN** `desktop_lifecycle_gate_status.observed_process_window_ownership.status` SHALL be `observed`
- **AND** the payload SHALL include `title_keyword`, `exe_path`, `runtime_ok`, `window_ok`, and the serialized read-only health result.

#### Scenario: Process/window observation remains read-only

- **WHEN** `observed_process_window_ownership` is returned
- **THEN** the workflow MUST NOT start, stop, restart, or supervise the PingAn process
- **AND** it MUST NOT write statefile ownership, lock ownership, submission ledger entries, trade audit artifacts, or order state
- **AND** `desktop_lifecycle_gate_status.side_effect_level` SHALL remain `none`.

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

### Requirement: Stable desktop trading dialog readiness SHALL expose read-only statefile lock status

The stable PingAn dialog readiness workflow SHALL expose a read-only `statefile_lock_status` object in `desktop_lifecycle_gate_status`.

#### Scenario: Caller checks dialog readiness without lifecycle lock ownership

- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(...)`
- **THEN** `desktop_lifecycle_gate_status.statefile_lock_status.status` SHALL be `not_acquired`
- **AND** the payload SHALL include `execution_mode=readonly_lock_status`, `lock_acquired=false`, `owner_token=null`, resolved artifact targets, and false write flags for statefile, event log, submission ledger, and trade audit writes.

#### Scenario: Statefile lock status remains read-only

- **WHEN** `statefile_lock_status` is returned
- **THEN** the workflow MUST NOT acquire locks, write owner tokens, write statefile data, append event logs, append submission ledger entries, write trade audit artifacts, or manage the desktop process
- **AND** `desktop_lifecycle_gate_status.side_effect_level` SHALL remain `none`.

