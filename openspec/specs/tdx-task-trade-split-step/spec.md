# tdx-task-trade-split-step Specification

## Purpose
TBD - created by archiving change add-task-trade-split-step-workflows. Update Purpose after archive.
## Requirements
### Requirement: Task split-step trading SHALL expose a stable submit-ready workflow
The system SHALL expose a stable task-facing workflow for pushing a buy request to the visible confirm boundary through the existing desktop trade submit-ready path.

#### Scenario: Caller runs task submit-ready with an order request
- **WHEN** a caller executes `TdxTaskManager.trade_submit_ready(...)`
- **THEN** the task workflow MUST invoke the stable desktop `submit_ready(...)` path
- **AND** the returned task result MUST include structured `trade_result` data from the underlying trade workflow

#### Scenario: Submit-ready task orchestrates optional environment refresh
- **WHEN** a caller executes the submit-ready task with `refresh_before_trade`
- **THEN** the task workflow MUST run the existing manager-backed refresh orchestration before invoking the desktop submit-ready path
- **AND** the task result MUST expose the refresh outcome

### Requirement: Task split-step trading SHALL expose a stable confirm-current workflow
The system SHALL expose a stable task-facing workflow for advancing the currently visible desktop trade confirm dialog through the existing confirm-current path.

#### Scenario: Caller runs task confirm-current without a new order request
- **WHEN** a caller executes `TdxTaskManager.trade_confirm_current(...)`
- **THEN** the task workflow MUST invoke the stable desktop `confirm_current(...)` path
- **AND** the task result MUST expose the underlying confirm summary and any result-dialog summary

#### Scenario: Confirm-current task does not require order-entry fields
- **WHEN** a caller executes the stable confirm-current task workflow
- **THEN** the workflow MUST NOT require `port`, `code`, `price`, or `quantity`

### Requirement: Task split-step trading SHALL preserve underlying trade safety and artifact visibility
The system SHALL keep task-facing split-step trade workflows aligned with the underlying stable trade management contract instead of creating a separate task-specific trade envelope.

#### Scenario: Submit-ready task preserves trade safety visibility
- **WHEN** a caller executes the stable task submit-ready workflow successfully
- **THEN** the task result MUST continue to expose the underlying `trade_safety` metadata through `trade_result`
- **AND** it MUST expose any returned artifact visibility without inventing task-only ledger behavior

#### Scenario: Confirm-current task preserves trade safety and artifact visibility
- **WHEN** a caller executes the stable task confirm-current workflow successfully
- **THEN** the task result MUST continue to expose the underlying `trade_safety` metadata through `trade_result`
- **AND** it MUST expose any returned result-dialog and artifact visibility from the underlying trade workflow

