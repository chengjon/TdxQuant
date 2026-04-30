## Purpose

定义稳定场景化 `task` 管理层，包括面向日常 workflow 的稳定 task 命令，以及围绕这些 workflow 的 task preset 快捷调用能力。
## Requirements
### Requirement: Task management SHALL provide a stable scenario-oriented entry layer above API manager
The system SHALL define a task layer above `TdxApiManager` for stable, scenario-oriented daily workflows rather than requiring users to compose raw API calls each time.

#### Scenario: Caller runs a watchlist overview task
- **WHEN** a caller provides a list of stock codes for routine batch overview
- **THEN** the task layer MUST support a stable task that orchestrates batch overview retrieval through manager-backed APIs

#### Scenario: Caller runs a sector formula scan task
- **WHEN** a caller provides a sector/block and a formula name
- **THEN** the task layer MUST support a stable task that first resolves sector constituents and then executes formula scanning through manager-backed APIs

#### Scenario: Caller runs a watchlist export task
- **WHEN** a caller provides a list of stock codes for routine batch overview export
- **THEN** the task layer MUST support a stable task that orchestrates manager-backed retrieval and writes structured export artifacts

#### Scenario: Caller runs a sector research export task
- **WHEN** a caller provides a sector/block for routine research export
- **THEN** the task layer MUST support a stable task that orchestrates manager-backed sector research and writes structured export artifacts

#### Scenario: Caller runs a trade buy workflow task
- **WHEN** a caller provides a stable desktop trading buy request through the task layer
- **THEN** the task layer MUST be able to orchestrate optional environment refresh and then invoke the dedicated trade management path

#### Scenario: Caller runs a trade submit-once workflow task
- **WHEN** a caller provides a stable desktop trading submit-once request through the task layer
- **THEN** the task layer MUST be able to orchestrate optional environment refresh and then invoke the dedicated trade management path

#### Scenario: Caller runs a guarded trade buy workflow task
- **WHEN** a caller provides a protected desktop trading buy request with precheck constraints through the task layer
- **THEN** the task layer MUST be able to run manager-backed prechecks before invoking the trade workflow and writing a structured task report

#### Scenario: Guarded trade buy includes formula precheck
- **WHEN** a caller provides a formula constraint for the guarded trade buy workflow
- **THEN** the task layer MUST be able to execute a manager-backed formula precheck before allowing the trade workflow to proceed

#### Scenario: Guarded trade buy appends to task ledger
- **WHEN** a guarded trade buy workflow completes with report artifacts
- **THEN** the task layer MUST be able to append summary entries to continuous ledger artifacts

#### Scenario: Caller runs a ledger summary task
- **WHEN** a caller requests a stable task workflow for inspecting continuous task ledger records
- **THEN** the task layer MUST be able to read ledger artifacts, apply filters, and return a structured summary view

#### Scenario: Caller runs a daily trade report task
- **WHEN** a caller requests a stable task workflow for daily aggregation of trade ledger records
- **THEN** the task layer MUST be able to filter ledger records by local trade date and return a structured aggregated report

#### Scenario: Caller runs a trade report lookup task
- **WHEN** a caller requests a stable task workflow for locating a single trade report from ledger records
- **THEN** the task layer MUST be able to resolve matching ledger entries and linked report artifacts

#### Scenario: Caller runs a trade period report task
- **WHEN** a caller requests a stable task workflow for aggregating trade ledger records across a date range
- **THEN** the task layer MUST be able to filter ledger records by inclusive local-date range and return a structured aggregated report

#### Scenario: Report CLI reuses stable task report workflows
- **WHEN** the CLI exposes a dedicated `report` namespace for report-oriented daily usage
- **THEN** the underlying report workflows MUST continue to be backed by the stable task-management layer rather than a separate duplicated logic path

### Requirement: Task CLI SHALL expose and execute presets for stable task workflows
The system SHALL expose a CLI preset layer for selected stable task workflows so callers can reuse fixed command-level defaults without duplicating long commands.

#### Scenario: Caller lists available task presets
- **WHEN** a caller executes the task preset listing command
- **THEN** the system MUST return the available preset names together with their mapped stable task command metadata

#### Scenario: Caller runs a guarded trade task preset
- **WHEN** a caller executes a named task preset whose target command is `guarded-trade-buy`
- **THEN** the system MUST resolve the preset defaults and run the existing guarded trade workflow through the stable task management path

#### Scenario: Caller runs a refresh task preset
- **WHEN** a caller executes a named task preset whose target command is `refresh-environment`
- **THEN** the system MUST resolve the preset defaults and run the existing refresh workflow through the stable task management path

#### Scenario: Explicit CLI arguments override task preset defaults
- **WHEN** a caller executes a named task preset and also provides overlapping CLI arguments explicitly
- **THEN** the system MUST prefer the explicit CLI argument values over the preset defaults

#### Scenario: Task preset points to an unsupported command
- **WHEN** a caller executes a task preset whose configured target is not a supported stable task preset command
- **THEN** the system MUST reject the request with an invalid-request style error instead of dispatching an unknown workflow

### Requirement: Task management SHALL expose runtime subscription watch as a stable task workflow
The system SHALL expose a stable runtime subscription watch workflow through `TdxTaskManager` and the `task` CLI group rather than requiring daily callers to orchestrate subscription sessions manually.

#### Scenario: Caller runs subscription watch through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable runtime watch workflow through `manager.subscription_watch(...)`

#### Scenario: Caller runs subscription watch through task CLI
- **WHEN** a caller invokes `task subscription-watch`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring direct session-level runtime calls

### Requirement: Task management SHALL pass stable desktop trade safety controls through trade tasks
The system SHALL allow stable trade-oriented task workflows to accept and forward the desktop trade safety controls already supported by the stable trade management layer.

#### Scenario: Caller runs trade buy task with safety controls
- **WHEN** a caller executes the stable `trade_buy` task workflow with `submission_key` or `max_price`
- **THEN** the task workflow MUST forward those values into the underlying stable desktop trade management call

#### Scenario: Caller runs trade submit-once task with safety controls
- **WHEN** a caller executes the stable `trade_submit_once` task workflow with `submission_key` or `max_price`
- **THEN** the task workflow MUST forward those values into the underlying stable desktop trade management call

#### Scenario: Caller runs guarded trade buy task with safety controls
- **WHEN** a caller executes the stable `guarded_trade_buy` task workflow with `submission_key` or `max_price`
- **THEN** the task workflow MUST preserve those values through its guarded prechecks and forward them into the underlying stable desktop trade step

### Requirement: Task preset execution SHALL preserve trade safety controls for stable trade tasks
The system SHALL allow preset-driven stable trade task execution to carry the same desktop trade safety controls while still preferring explicit CLI overrides.

#### Scenario: Task run preserves explicit safety-control overrides
- **WHEN** a caller executes `task run --preset ...` for a stable trade-oriented task and also provides explicit `submission_key` or `max_price`
- **THEN** the resolved task workflow MUST receive those explicit values even if the preset defines different defaults

### Requirement: Task management SHALL expose split-step desktop trade workflows as stable task commands
The system SHALL expose stable task-layer commands for the existing desktop trade split-step workflows so daily callers can reuse the confirm boundary without dropping to the lower-level trade namespace.

#### Scenario: Caller runs task trade-submit-ready
- **WHEN** a caller invokes `task trade-submit-ready`
- **THEN** the CLI MUST dispatch the workflow through `TdxTaskManager.trade_submit_ready(...)`

#### Scenario: Caller runs task trade-confirm-current
- **WHEN** a caller invokes `task trade-confirm-current`
- **THEN** the CLI MUST dispatch the workflow through `TdxTaskManager.trade_confirm_current(...)`

### Requirement: Task preset execution SHALL support split-step desktop trade workflows
The system SHALL allow `task run --preset ...` to target the stable split-step desktop trade workflows while preserving explicit CLI overrides.

#### Scenario: Task run executes a submit-ready preset
- **WHEN** a caller executes a named task preset whose target command is `trade-submit-ready`
- **THEN** the system MUST resolve the preset defaults and run the stable submit-ready workflow through the task-management path

#### Scenario: Task run executes a confirm-current preset
- **WHEN** a caller executes a named task preset whose target command is `trade-confirm-current`
- **THEN** the system MUST resolve the preset defaults and run the stable confirm-current workflow through the task-management path

#### Scenario: Confirm-current preset does not require order-entry fields
- **WHEN** a caller executes a named task preset whose target command is `trade-confirm-current`
- **THEN** preset resolution MUST NOT reject the request for missing `port`, `code`, `price`, or `quantity`
- **AND** any explicitly provided boundary arguments MUST still override preset defaults

### Requirement: Task management SHALL expose trade audit lookup as a stable task workflow
The system SHALL expose a stable task-layer workflow for resolving immutable trade-audit artifacts without requiring callers to inspect runtime directories manually.

#### Scenario: Caller runs a trade audit lookup task
- **WHEN** a caller requests a stable task workflow for locating one or more desktop trade audit artifacts
- **THEN** the task layer MUST be able to scan audit artifacts, apply filters, and return a structured lookup result

### Requirement: Task management SHALL expose trade audit daily and period aggregation as stable workflows
The system SHALL expose stable task-layer workflows for aggregating immutable trade-audit artifacts by local trade date and by inclusive date range.

#### Scenario: Caller runs a trade audit daily report task
- **WHEN** a caller requests a stable daily report workflow for desktop trade audits
- **THEN** the task layer MUST be able to filter audit artifacts by one local date and return structured aggregation data

#### Scenario: Caller runs a trade audit period report task
- **WHEN** a caller requests a stable period report workflow for desktop trade audits
- **THEN** the task layer MUST be able to filter audit artifacts by an inclusive local-date range and return structured aggregation data

### Requirement: Task preset execution SHALL expose stable split-step desktop trade defaults for daily use
The system SHALL expose stable task presets for the existing split-step desktop trade workflows so daily callers can reuse fixed environment defaults without retyping the full task command.

#### Scenario: Caller lists split-step task presets
- **WHEN** a caller lists task presets after stable split-step desktop trade workflows are available
- **THEN** the preset registry MUST include stable presets for `trade-submit-ready` and `trade-confirm-current`

#### Scenario: Caller runs a split-step task preset
- **WHEN** a caller executes a named task preset whose target command is `trade-submit-ready` or `trade-confirm-current`
- **THEN** the system MUST resolve the preset defaults and run the existing stable task workflow through the task-management path

### Requirement: Task management SHALL allow stable trade-audit daily and period workflows to filter by multiple statuses
The system SHALL allow the stable trade-audit daily and period workflows to accept a list of statuses interpreted with OR semantics, in addition to the existing single-status filter.

#### Scenario: Caller runs trade-audit daily report with multiple statuses
- **WHEN** a caller provides more than one status to the stable trade-audit daily report workflow
- **THEN** the workflow MUST return entries whose audit status matches any provided status

#### Scenario: Caller runs trade-audit period report with multiple statuses
- **WHEN** a caller provides more than one status to the stable trade-audit period report workflow
- **THEN** the workflow MUST return entries whose audit status matches any provided status

#### Scenario: Caller mixes single-status and multi-status filters
- **WHEN** a caller provides both the single-status filter and the multi-status filter in the same stable trade-audit workflow call
- **THEN** the workflow MUST reject the request as invalid instead of guessing precedence

### Requirement: Task management SHALL support multi-method OR filtering for stable trade-audit daily and period workflows
The system SHALL allow the stable trade-audit daily and period workflows to filter immutable audit artifacts by either one method or a set of methods using OR semantics while preserving current single-method calls.

#### Scenario: Caller requests a trade-audit report with multiple methods
- **WHEN** a caller executes the stable trade-audit daily or period workflow with `methods=[buy_submit_once, confirm_current]`
- **THEN** the workflow MUST include entries whose trade-audit method matches any listed method and exclude entries outside that set

#### Scenario: Caller mixes single-method and multi-method filters
- **WHEN** a caller executes the stable trade-audit daily or period workflow with both `method` and `methods`
- **THEN** the workflow MUST reject the request as invalid instead of guessing precedence

