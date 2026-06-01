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

### Requirement: Task preset execution SHALL support static block read watchlist export presets
The system SHALL allow the existing task preset layer to target `block-read-watchlist-export` so daily callers can reuse fixed export defaults without retyping the full command.

#### Scenario: Caller runs a block read watchlist export preset
- **WHEN** a caller executes a named task preset whose target command is `block-read-watchlist-export`
- **THEN** the system MUST resolve the preset defaults and run the existing stable block-read-watchlist-export workflow through the task-management path

#### Scenario: Explicit export preset CLI arguments override preset defaults
- **WHEN** a caller executes a `block-read-watchlist-export` preset and also provides explicit `block_code`, `export_output`, or `overwrite` CLI arguments
- **THEN** the system MUST prefer those explicit CLI argument values over the preset defaults

#### Scenario: Export preset is missing required fields
- **WHEN** a caller executes a `block-read-watchlist-export` preset that omits `block_code` or `export_output`
- **THEN** the system MUST reject the request as invalid instead of dispatching an incomplete export workflow

### Requirement: Task preset execution SHALL support static block read watchlist presets
The system SHALL allow the existing task preset layer to target `block-read-watchlist` so daily callers can reuse a fixed `block_code` default for the stable snapshot task without retyping the full command.

#### Scenario: Caller runs a block read watchlist preset
- **WHEN** a caller executes a named task preset whose target command is `block-read-watchlist`
- **THEN** the system MUST resolve the preset defaults and run the existing stable block-read-watchlist workflow through the task-management path

#### Scenario: Explicit block read watchlist preset CLI arguments override preset defaults
- **WHEN** a caller executes a `block-read-watchlist` preset and also provides an explicit `block_code` CLI argument
- **THEN** the system MUST prefer that explicit CLI argument value over the preset default

#### Scenario: Block read watchlist preset is missing required fields
- **WHEN** a caller executes a `block-read-watchlist` preset that omits `block_code`
- **THEN** the system MUST reject the request as invalid instead of dispatching an incomplete snapshot workflow

### Requirement: Task preset execution SHALL support static block read full presets
The system SHALL allow the existing task preset layer to target `block-read-full` so daily callers can reuse a fixed `block_code` default for the stable diagnostics task without retyping the full command.

#### Scenario: Caller runs a block read full preset
- **WHEN** a caller executes a named task preset whose target command is `block-read-full`
- **THEN** the system MUST resolve the preset defaults and run the existing stable block-read-full workflow through the task-management path

#### Scenario: Explicit block read full preset CLI arguments override preset defaults
- **WHEN** a caller executes a `block-read-full` preset and also provides an explicit `block_code` CLI argument
- **THEN** the system MUST prefer that explicit CLI argument value over the preset default

#### Scenario: Block read full preset is missing required fields
- **WHEN** a caller executes a `block-read-full` preset that omits `block_code`
- **THEN** the system MUST reject the request as invalid instead of dispatching an incomplete diagnostics workflow

### Requirement: Task management SHALL expose runtime subscription watch as a stable task workflow
The system SHALL expose a stable runtime subscription watch workflow through `TdxTaskManager` and the `task` CLI group rather than requiring daily callers to orchestrate subscription sessions manually.

#### Scenario: Caller runs subscription watch through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable runtime watch workflow through `manager.subscription_watch(...)`

#### Scenario: Caller runs subscription watch through task CLI
- **WHEN** a caller invokes `task subscription-watch`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring direct session-level runtime calls

### Requirement: Task management SHALL expose block sync as a stable task workflow
The system SHALL expose a stable `block-sync` task workflow through `TdxTaskManager` and the `task` CLI group so daily callers can reuse provider-level block synchronization without composing raw manager calls manually.

#### Scenario: Caller runs block sync through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable block sync workflow through `manager.block_sync(...)`
- **AND** the task workflow MUST delegate to `manager.block.sync_watchlist(...)` rather than reimplementing provider-level synchronization logic

#### Scenario: Caller runs block sync through task CLI
- **WHEN** a caller invokes `task block-sync`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring the caller to invoke `api block-sync` directly

#### Scenario: Task block sync preserves provider-level sync summary and attaches task metadata
- **WHEN** a caller executes the stable block sync task workflow
- **THEN** the returned result MUST preserve the provider-level `data.sync`, `data.block_mutation`, and `artifacts` fields
- **AND** the task layer MUST only append standard task metadata and timing metadata instead of redefining a second block-sync result schema

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

### Requirement: Task management SHALL expose block read watchlist as a stable task workflow
The system SHALL expose a stable `block-read-watchlist` task workflow through `TdxTaskManager` and the `task` CLI group so daily callers can reuse provider-level watchlist snapshot reads without composing raw manager calls manually.

#### Scenario: Caller runs block read watchlist through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable block read watchlist workflow through `manager.block_read_watchlist(...)`
- **AND** the task workflow MUST delegate to `manager.block.read_watchlist_snapshot(...)` rather than reimplementing provider-level snapshot normalization logic

#### Scenario: Caller runs block read watchlist through task CLI
- **WHEN** a caller invokes `task block-read-watchlist`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring the caller to invoke `api block-read-watchlist` directly

#### Scenario: Task block read watchlist preserves provider-level snapshot and attaches task metadata
- **WHEN** a caller executes the stable block read watchlist task workflow
- **THEN** the returned result MUST preserve the provider-level `data.snapshot`, `artifacts`, and `warnings` fields
- **AND** the task layer MUST only append standard task metadata and timing metadata instead of redefining a second block-read-watchlist result schema

### Requirement: Task management SHALL expose block read full as a stable task workflow
The system SHALL expose a stable `block-read-full` task workflow through `TdxTaskManager` and the `task` CLI group so daily callers can inspect a higher-level diagnostics view above provider-level block watchlist snapshots without composing raw manager calls manually.

#### Scenario: Caller runs block read full through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable block read full workflow through `manager.block_read_full(...)`
- **AND** the task workflow MUST delegate to `manager.block.read_watchlist_snapshot(...)` rather than issuing a second raw block read

#### Scenario: Caller runs block read full through task CLI
- **WHEN** a caller invokes `task block-read-full`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring the caller to invoke lower-level provider commands directly

#### Scenario: Task block read full preserves canonical snapshot and appends diagnostics summary
- **WHEN** a caller executes the stable block read full task workflow and the provider-level snapshot succeeds
- **THEN** the returned result MUST preserve the provider-level `data.snapshot`, `artifacts`, and `warnings` fields
- **AND** the task layer MUST append task-level `data.read_full` containing diagnostics summary fields derived from the successful snapshot
- **AND** the task layer MUST continue to append only standard task metadata and timing metadata rather than redefining a second provider-level block-read schema

#### Scenario: Task block read full preserves provider failure contract
- **WHEN** a caller executes the stable block read full task workflow and the provider-level snapshot fails
- **THEN** the task layer MUST preserve the provider failure contract and MUST NOT fabricate `data.read_full`

### Requirement: Task management SHALL expose block read watchlist export as a stable task workflow
The system SHALL expose a stable `block-read-watchlist-export` task workflow through `TdxTaskManager` and the `task` CLI group so daily callers can safely export provider-level watchlist snapshots to a local JSON file without composing raw manager calls and file-write logic manually.

#### Scenario: Caller runs block read watchlist export through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable block read watchlist export workflow through `manager.block_read_watchlist_export(...)`
- **AND** the task workflow MUST delegate snapshot retrieval to `manager.block.read_watchlist_snapshot(...)` rather than reimplementing provider-level snapshot normalization logic

#### Scenario: Caller runs block read watchlist export through task CLI
- **WHEN** a caller invokes `task block-read-watchlist-export`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring the caller to manually combine `task block-read-watchlist` with ad hoc file writing

#### Scenario: Task block read watchlist export preserves provider snapshot and appends thin export metadata
- **WHEN** a caller executes the stable block read watchlist export workflow successfully
- **THEN** the returned result MUST preserve the provider-level `data.snapshot`, `artifacts`, and `warnings` fields
- **AND** the task layer MUST append a thin `data.export` object containing file-output metadata instead of redefining a second block-read-watchlist snapshot schema

#### Scenario: Task block read watchlist export retains snapshot on export failure
- **WHEN** snapshot retrieval succeeds but output-path validation or file writing fails
- **THEN** the returned result MUST remain a failure
- **AND** the result MUST continue to preserve `data.snapshot`
- **AND** the task layer MUST expose only failure-context export metadata instead of success-only file-size or overwrite fields

### Requirement: Task management SHALL expose trade audit cross-ledger query as a read-only task
The system SHALL expose the trade audit cross-ledger query through `TdxTaskManager` and the `task` CLI namespace as a read-only workflow. The workflow MUST attach task metadata and MUST NOT mutate trade audit, submission ledger, or task ledger sources.

#### Scenario: Manager-backed query returns task metadata
- **WHEN** a caller invokes the trade audit cross-ledger query through `TdxTaskManager`
- **THEN** the result includes task metadata with the query task name
- **AND** the result includes source paths and query summary metadata

#### Scenario: CLI parses cross-ledger query options
- **WHEN** a caller parses `task trade-audit-cross-ledger-query` with audit, submission ledger, task ledger, filter, cache, and export arguments
- **THEN** those arguments are available on the parsed namespace for dispatch to the manager-backed task

### Requirement: Task presets SHALL include a safe block sync write-policy plan

The task preset registry SHALL include a stable preset for planning a block watchlist sync with an explicit dry-run write policy.

#### Scenario: Caller runs the block sync plan preset

- **WHEN** a caller executes `task run --preset plan-zxg-block-sync-merge`
- **THEN** the task runner MUST resolve the preset to `block-sync`
- **AND** the resolved options MUST include `write_policy=merge_dry_run`
- **AND** the preset MUST not require live provider writes by default

### Requirement: Trade submit-once task SHALL expose explicit order side

The task-level submit-once workflow SHALL accept an explicit buy/sell side selector while keeping buy as the default.

#### Scenario: Caller runs a sell submit-once task

- **WHEN** a caller runs the trade submit-once task with `side=sell`
- **THEN** the task MUST route through the existing Ping An sell execution chain
- **AND** the task result input MUST preserve `side=sell`
- **AND** the task MUST continue to apply existing refresh and safety-control handling

#### Scenario: Caller omits submit-once task side

- **WHEN** a caller runs the trade submit-once task without a side
- **THEN** the task MUST preserve the previous buy submit-once behavior

### Requirement: Task management SHALL expose a stable trade sell workflow

The task layer SHALL provide a `trade-sell` workflow that mirrors `trade-buy` for Ping An desktop sell operations.

#### Scenario: Caller runs a trade sell workflow task

- **WHEN** a caller provides a stable desktop trading sell request through the task layer
- **THEN** the task layer MUST be able to orchestrate optional environment refresh and then invoke the dedicated Ping An sell management path
- **AND** the task result MUST preserve the input, refresh result, trade result, artifacts, and result-dialog summary

#### Scenario: Trade sell task aborts on refresh failure

- **WHEN** a trade sell task requests environment refresh and refresh fails
- **THEN** the task MUST return the refresh failure without invoking the sell workflow

### Requirement: Trade submit-once task SHALL route sell side through sell submit-once identity

The task-level submit-once workflow SHALL route explicit sell-side submit-once requests through the dedicated Ping An sell submit-once manager identity.

#### Scenario: Caller runs a sell submit-once task

- **WHEN** a caller runs `trade_submit_once` with `side=sell`
- **THEN** the task MUST call `TdxTradeManager.pingan.sell_submit_once`
- **AND** the task result input MUST preserve `side=sell`
- **AND** refresh and safety controls such as `submission_key` and `max_price` MUST continue to apply

#### Scenario: Caller omits submit-once task side

- **WHEN** a caller runs `trade_submit_once` without a side
- **THEN** the task MUST preserve the existing buy submit-once behavior

### Requirement: Task preset registry SHALL expose a stable trade-sell default preset

The task preset registry SHALL expose a stable preset for the existing `trade-sell` task workflow without changing sell execution behavior.

#### Scenario: Caller resolves the task sell default preset

- **WHEN** a caller resolves `task-sell-default`
- **THEN** the preset MUST target the existing `trade-sell` task command
- **AND** it MUST use the existing `trade_sell` task profile
- **AND** real sell execution MUST continue to require explicit order parameters and existing trade safety controls

### Requirement: Task preset registry SHALL expose a side-explicit sell submit-once preset

The task preset registry SHALL expose a stable sell-side submit-once preset that targets the existing `trade-submit-once` task workflow without changing submit-once execution behavior.

#### Scenario: Caller resolves the sell submit-once default preset

- **WHEN** a caller resolves `sell-submit-once-default`
- **THEN** the preset MUST target the existing `trade-submit-once` task command
- **AND** it MUST set `side=sell`
- **AND** it MUST continue to require explicit order parameters and existing trade safety controls for real execution
- **AND** it MUST NOT imply a separate sell submit-once desktop primitive exists

### Requirement: Task trade workflows SHALL forward lifecycle owner-lock execution guard options

Stable PingAn task trade workflows SHALL accept optional lifecycle owner-lock guard options and forward them to the selected PingAn manager execution method without implementing a separate guard.

#### Scenario: Task trade-buy forwards the opt-in guard

- **WHEN** a caller executes `TdxTaskManager.trade_buy(...)` with `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTradeManager.pingan.buy(...)`
- **AND** the task MUST preserve existing trade safety controls such as `submission_key` and `max_price`.

#### Scenario: Task trade-sell forwards the opt-in guard

- **WHEN** a caller executes `TdxTaskManager.trade_sell(...)` with `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTradeManager.pingan.sell(...)`
- **AND** the task MUST preserve existing trade safety controls such as `submission_key` and `max_price`.

#### Scenario: Task trade-submit-once forwards the opt-in guard for both sides

- **WHEN** a caller executes `TdxTaskManager.trade_submit_once(...)` with `side=buy` or `side=sell` and `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to the selected buy-submit-once or sell-submit-once PingAn manager method.

### Requirement: Task owner-lock execution guard SHALL remain delegated safety evidence

The task layer SHALL delegate owner-lock execution guard enforcement to the PingAn manager execution methods and SHALL NOT perform lifecycle control itself.

#### Scenario: Task guard forwarding remains bounded

- **WHEN** task trade workflows receive lifecycle owner-lock guard options
- **THEN** the task layer MUST NOT acquire or release owner locks
- **AND** it MUST NOT write lifecycle statefile/lock artifacts directly
- **AND** it MUST NOT start, stop, restart, kill, supervise, or back off PingAn processes.

### Requirement: Task preset execution SHALL preserve lifecycle owner-lock guard options for trade tasks

Task preset execution SHALL preserve preset-provided lifecycle owner-lock guard options and expose them to the resolved task trade command namespace.

#### Scenario: Preset-provided guard options are preserved

- **WHEN** a task preset for `trade-buy`, `trade-sell`, or `trade-submit-once` includes lifecycle owner-lock guard options
- **THEN** the resolved namespace MUST retain those values when the caller does not provide explicit CLI overrides.

#### Scenario: Missing stale timeout uses the stable default

- **WHEN** the resolved task namespace has no lifecycle stale timeout
- **THEN** owner-lock guard forwarding MUST use the stable `300.0` second default instead of failing.

### Requirement: Task preset owner-lock guard forwarding SHALL remain bounded

Task preset owner-lock guard forwarding SHALL remain argument forwarding to existing task trade workflows.

#### Scenario: Preset guard forwarding remains bounded

- **WHEN** task preset execution forwards lifecycle owner-lock guard options
- **THEN** it MUST NOT acquire or release owner locks
- **AND** it MUST NOT write lifecycle statefile/lock artifacts directly
- **AND** it MUST NOT start, stop, restart, kill, supervise, or back off PingAn processes.

### Requirement: Guarded trade-buy task SHALL forward lifecycle owner-lock guard options

The guarded PingAn trade-buy task workflow SHALL accept optional lifecycle owner-lock guard options and forward them to the delegated `trade_buy` workflow.

#### Scenario: Guarded trade-buy forwards owner-lock guard options

- **WHEN** a caller executes `TdxTaskManager.guarded_trade_buy(...)` with `require_lifecycle_owner_lock=true`
- **THEN** the guarded workflow MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTaskManager.trade_buy(...)`
- **AND** it MUST preserve existing guarded prechecks and trade safety controls such as `submission_key`, `max_price`, and `max_snapshot_price`.

### Requirement: Guarded owner-lock forwarding SHALL remain delegated safety evidence

Guarded trade-buy owner-lock forwarding SHALL remain argument forwarding to the delegated trade execution workflow.

#### Scenario: Guarded forwarding remains bounded

- **WHEN** guarded trade-buy receives lifecycle owner-lock guard options
- **THEN** it MUST NOT acquire or release owner locks
- **AND** it MUST NOT write lifecycle statefile/lock artifacts directly
- **AND** it MUST NOT start, stop, restart, kill, supervise, or back off PingAn processes.

### Requirement: Task confirm-current SHALL forward lifecycle owner-lock guard options
`TdxTaskManager.trade_confirm_current(...)` SHALL accept optional lifecycle owner-lock guard options and forward them to `TdxTradeManager.pingan.confirm_current(...)`.

#### Scenario: Task confirm-current forwards owner-lock guard options
- **WHEN** a caller executes `TdxTaskManager.trade_confirm_current(...)` with lifecycle statefile path, owner token, stale timeout, and `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass those values to `TdxTradeManager.pingan.confirm_current(...)`
- **AND** the task MUST NOT perform lifecycle owner-lock acquire/release or write statefile/lock artifacts itself.

#### Scenario: Task confirm-current default dispatch remains unchanged
- **WHEN** a caller executes `TdxTaskManager.trade_confirm_current(...)` without lifecycle owner-lock guard options
- **THEN** the task MUST keep the existing confirm-current manager call shape.

### Requirement: Task submit-ready SHALL forward lifecycle owner-lock guard options
`TdxTaskManager.trade_submit_ready(...)` SHALL accept optional lifecycle owner-lock guard options and forward them to `TdxTradeManager.pingan.submit_ready(...)`.

#### Scenario: Task submit-ready forwards owner-lock guard options
- **WHEN** a caller executes `TdxTaskManager.trade_submit_ready(...)` with lifecycle statefile path, owner token, stale timeout, and `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass those values to `TdxTradeManager.pingan.submit_ready(...)`
- **AND** the task MUST NOT perform lifecycle owner-lock acquire/release or write statefile/lock artifacts itself.

#### Scenario: Task submit-ready default dispatch remains unchanged
- **WHEN** a caller executes `TdxTaskManager.trade_submit_ready(...)` without lifecycle owner-lock guard options
- **THEN** the task MUST keep the existing submit-ready manager call shape.

### Requirement: Task confirm-current SHALL forward broker readiness guard
Task confirm-current SHALL accept the broker readiness guard option and forward it to the PingAn manager confirm-current method without evaluating broker health in the task layer.

#### Scenario: Task confirm-current forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_confirm_current(...)` is called with `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.confirm_current(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.

### Requirement: Task buy and sell SHALL forward broker readiness guard
Task buy and sell workflows SHALL accept the broker readiness guard option and forward it to the PingAn manager buy/sell methods without evaluating broker health in the task layer.

#### Scenario: Task buy forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_buy(...)` is called with `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.buy(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.

#### Scenario: Task sell forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_sell(...)` is called with `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.sell(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.

### Requirement: Task submit-once SHALL forward broker readiness guard
Task submit-once workflow SHALL accept the broker readiness guard option and forward it to the side-specific PingAn manager submit-once method without evaluating broker health in the task layer.

#### Scenario: Task buy submit-once forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_submit_once(...)` is called with `side=buy` and `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.buy_submit_once(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.

#### Scenario: Task sell submit-once forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_submit_once(...)` is called with `side=sell` and `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.sell_submit_once(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.

### Requirement: Task management SHALL expose PingAn promotion readiness rollup as a stable read-only workflow

The task manager SHALL provide a stable PingAn promotion readiness rollup workflow that reads existing JSON evidence artifacts and summarizes D-07/D-08 promotion gates without executing PingAn trading workflows.

#### Scenario: Caller generates a partial promotion readiness rollup

- **WHEN** a caller provides preflight, dialog readiness, and acceptance coverage evidence paths
- **THEN** the task result SHALL include `promotion_readiness_rollup`
- **AND** the rollup SHALL identify `schema=tdx.desktop_trade.pingan_promotion_readiness_rollup.v1`
- **AND** it SHALL include named gate statuses for provider/broker ownership, safety gates, desktop lifecycle, audit evidence, live/manual acceptance, and acceptance evidence
- **AND** it SHALL include completed and incomplete gate lists.

#### Scenario: Caller generates a complete promotion readiness rollup

- **WHEN** all required gate evidence explicitly reports complete or ready status
- **THEN** the rollup SHALL report `status=complete`
- **AND** it SHALL keep `promotion_status_transition_executed=false`.

#### Scenario: Missing evidence remains visible

- **WHEN** a caller omits one or more evidence paths
- **THEN** the rollup SHALL mark the corresponding gates incomplete
- **AND** it SHALL include `missing_evidence_kinds`.

#### Scenario: Rollup remains read-only

- **WHEN** the rollup task runs
- **THEN** it SHALL report `execution_mode=readonly_evidence_rollup`
- **AND** it SHALL report `side_effect_level=none`
- **AND** it SHALL report `order_submitted=false`
- **AND** it SHALL report `control_dispatch_executed=false`.

### Requirement: Task management SHALL gate PingAn promotion evidence freshness

The task manager SHALL allow the PingAn promotion readiness rollup to reject stale evidence artifacts when a freshness cutoff is provided.

#### Scenario: Fresh evidence remains eligible

- **WHEN** a caller supplies a freshness cutoff and evidence files are newer than the cutoff
- **THEN** the rollup SHALL preserve the existing gate status evaluation
- **AND** it SHALL report the evidence as fresh.

#### Scenario: Stale evidence remains visible but incomplete

- **WHEN** a caller supplies a freshness cutoff and one or more evidence files are older than the cutoff
- **THEN** the rollup SHALL mark the affected evidence stale
- **AND** it SHALL keep the affected gate incomplete
- **AND** it SHALL expose the stale evidence path and source kind.

#### Scenario: No freshness cutoff preserves existing behavior

- **WHEN** a caller omits the freshness cutoff
- **THEN** the rollup SHALL behave as the existing read-only evidence aggregator
- **AND** it SHALL not invent freshness failures.

### Requirement: Task management SHALL persist PingAn promotion readiness rollup artifacts on request

The task manager SHALL allow callers to write the read-only PingAn promotion readiness rollup to a caller-provided JSON path.

#### Scenario: Caller writes a rollup artifact

- **WHEN** a caller provides `json_output_path`
- **THEN** the task result SHALL include `promotion_readiness_rollup_artifact`
- **AND** the JSON file SHALL contain the rollup payload and task metadata
- **AND** the artifact metadata SHALL include the written path.

#### Scenario: Caller omits artifact path

- **WHEN** a caller omits `json_output_path`
- **THEN** the task SHALL behave as the existing in-memory read-only rollup
- **AND** it SHALL not write a default artifact file.

#### Scenario: Artifact write failure is explicit

- **WHEN** the requested artifact cannot be written
- **THEN** the task SHALL return `INVALID_REQUEST`
- **AND** it SHALL not execute broker, desktop, trade, report, or catalog workflows.

### Requirement: Task management SHALL load PingAn promotion readiness evidence manifests

The task manager SHALL allow callers to supply a read-only evidence manifest for PingAn promotion readiness rollups.

#### Scenario: Caller provides manifest evidence paths

- **WHEN** a caller provides `evidence_manifest_path`
- **THEN** the task SHALL load preflight, dialog readiness, acceptance coverage, and freshness cutoff values from the manifest
- **AND** it SHALL build the existing read-only promotion readiness rollup from those resolved values
- **AND** the result SHALL include `evidence_manifest` metadata.

#### Scenario: Explicit arguments override manifest values

- **WHEN** the manifest provides an evidence value and the caller also provides the same value directly
- **THEN** the direct caller-provided value SHALL take precedence.

#### Scenario: Expected gate metadata is reported

- **WHEN** the manifest includes `expected_gates`
- **THEN** the rollup SHALL report expected gates and missing expected gates
- **AND** it SHALL NOT execute additional workflows to satisfy those gates.

### Requirement: PingAn promotion readiness rollup preset SHALL resolve a safe sample manifest

The task preset registry SHALL provide a stable read-only preset for the PingAn promotion readiness rollup sample manifest.

#### Scenario: Task preset resolves the sample manifest path

- **GIVEN** the task preset registry contains `plan-pingan-promotion-readiness`
- **WHEN** an operator invokes `task run --preset plan-pingan-promotion-readiness`
- **THEN** the preset SHALL resolve to task command `pingan-promotion-readiness-rollup`
- **AND** the preset SHALL use API profile `safe_read`
- **AND** the preset SHALL provide `evidence_manifest_path` pointing at the sample manifest
- **AND** the preset SHALL NOT provide a default `json_output_path`
- **AND** direct preflight, dialog readiness, and acceptance coverage paths SHALL remain unset unless the caller explicitly overrides them.

#### Scenario: Sample preset registration remains read-only by default

- **GIVEN** the sample preset points at an example manifest
- **WHEN** the preset is resolved for catalog planning or parser dispatch tests
- **THEN** no provider, desktop, trade, report, or bundle workflow SHALL be executed as part of preset discovery.

### Requirement: PingAn readiness rollup SHALL expose a fail-closed implemented-status promotion decision

`TdxTaskManager.pingan_promotion_readiness_rollup` SHALL include a read-only implemented-status promotion decision derived from the existing readiness rollup evidence.

#### Scenario: Complete non-sample evidence is eligible for manual implemented-status review

- **GIVEN** the rollup has complete provider/broker ownership, safety gate, desktop lifecycle, audit evidence, live/manual acceptance, and combined acceptance evidence
- **AND** the evidence has no source errors, missing evidence, stale evidence, missing expected gates, or sample manifest marker
- **WHEN** the task builds `promotion_readiness_rollup`
- **THEN** `implemented_status_promotion_decision.decision` SHALL be `eligible_for_review`
- **AND** `implemented_status_promotion_decision.implemented_status_eligible` SHALL be `true`
- **AND** `implemented_status_promotion_decision.manual_status_review_required` SHALL be `true`
- **AND** `implemented_status_promotion_decision.function_tree_status_transition_executed` SHALL be `false`.

#### Scenario: Missing or incomplete evidence blocks implemented-status review

- **GIVEN** one or more required readiness gates are incomplete
- **WHEN** the task builds `promotion_readiness_rollup`
- **THEN** the decision SHALL be `blocked`
- **AND** `implemented_status_eligible` SHALL be `false`
- **AND** `blocked_reasons` SHALL include `incomplete_required_gates`.

#### Scenario: Stale or unreadable evidence blocks implemented-status review

- **GIVEN** source evidence is stale or unreadable
- **WHEN** the task builds `promotion_readiness_rollup`
- **THEN** the decision SHALL be `blocked`
- **AND** `blocked_reasons` SHALL include `stale_evidence` or `source_errors`.

#### Scenario: Sample manifest blocks implemented-status review

- **GIVEN** the evidence manifest is marked as example-only or sample-only
- **WHEN** the task builds `promotion_readiness_rollup`
- **THEN** the decision SHALL be `blocked`
- **AND** `blocked_reasons` SHALL include `sample_manifest`
- **AND** the decision SHALL state that sample evidence cannot satisfy D-07/D-08 implemented status.

### Requirement: PingAn promotion readiness SHALL require source evidence schema contracts for implemented-status review

`TdxTaskManager.pingan_promotion_readiness_rollup` SHALL verify the provenance contract of each source evidence artifact before the implemented-status promotion decision can become eligible for review.

#### Scenario: Valid producer schemas satisfy the evidence contract

- **GIVEN** preflight evidence includes `promotion_gate_status.schema_version=tdx.desktop_trade.pingan_promotion_gate_status.v1`
- **AND** dialog readiness evidence includes `desktop_lifecycle_gate_status.schema_version=tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1`
- **AND** acceptance coverage evidence includes `acceptance_outcome_coverage_status.schema=tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`
- **WHEN** the rollup builds `evidence_contract_status`
- **THEN** `evidence_contract_status.status` SHALL be `verified`
- **AND** `evidence_contract_status.invalid_source_kinds` SHALL be empty.

#### Scenario: Complete-looking schema-less evidence is not eligible for implemented-status review

- **GIVEN** source evidence contains complete-looking gate fields
- **BUT** one or more source evidence objects do not carry the expected producer schema
- **WHEN** the rollup builds `implemented_status_promotion_decision`
- **THEN** `evidence_contract_status.status` SHALL be `unverified`
- **AND** `implemented_status_promotion_decision.decision` SHALL be `blocked`
- **AND** `implemented_status_promotion_decision.blocked_reasons` SHALL include `unverified_evidence_contract`.

#### Scenario: Schema mismatch blocks implemented-status review

- **GIVEN** a source evidence object carries a schema key that does not match the expected producer schema
- **WHEN** the rollup builds `implemented_status_promotion_decision`
- **THEN** the corresponding source kind SHALL be listed in `evidence_contract_status.invalid_source_kinds`
- **AND** `blocked_reasons` SHALL include `unverified_evidence_contract`.

### Requirement: PingAn promotion readiness SHALL require artifact provenance for implemented-status review

`TdxTaskManager.pingan_promotion_readiness_rollup` SHALL verify artifact provenance metadata for each source evidence file before the implemented-status promotion decision can become eligible for review.

#### Scenario: Valid artifact provenance satisfies provenance gate

- **GIVEN** each source evidence file contains `artifact_provenance.schema=tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- **AND** each provenance object carries the matching source kind, expected evidence schema, and allowed producer
- **WHEN** the rollup builds `artifact_provenance_status`
- **THEN** `artifact_provenance_status.status` SHALL be `verified`
- **AND** `artifact_provenance_status.invalid_source_kinds` SHALL be empty.

#### Scenario: Schema-valid but provenance-less evidence is blocked

- **GIVEN** source evidence contains complete gates and valid producer schemas
- **BUT** one or more source files do not contain valid `artifact_provenance`
- **WHEN** the rollup builds `implemented_status_promotion_decision`
- **THEN** `artifact_provenance_status.status` SHALL be `unverified`
- **AND** `implemented_status_promotion_decision.decision` SHALL be `blocked`
- **AND** `implemented_status_promotion_decision.blocked_reasons` SHALL include `unverified_artifact_provenance`.

#### Scenario: Provenance mismatch is reported per source kind

- **GIVEN** a source evidence file has an artifact provenance object with mismatched source kind, evidence schema, or unsupported producer
- **WHEN** the rollup builds `artifact_provenance_status`
- **THEN** the source kind SHALL be listed in `artifact_provenance_status.invalid_source_kinds`
- **AND** the source status SHALL expose a reason for the mismatch.

### Requirement: PingAn live/manual acceptance recorder SHALL create controlled acceptance artifacts

`TdxTaskManager.pingan_live_manual_acceptance(...)` SHALL create a controlled `tdx.desktop_trade.pingan_live_manual_acceptance.v1` JSON artifact from explicit operator-provided outcomes.

#### Scenario: Recorder writes complete manual acceptance artifact

- **GIVEN** a caller provides output path, operator, environment, and all required outcomes
- **WHEN** `TdxTaskManager.pingan_live_manual_acceptance(...)` runs with `dry_run=false`
- **THEN** it SHALL write a JSON artifact with `schema=tdx.desktop_trade.pingan_live_manual_acceptance.v1`
- **AND** the artifact SHALL include `operator`, `environment`, `accepted_at`, and accepted outcomes for `confirmed`, `rejected`, `failed`, and `exception`
- **AND** the result data SHALL include `live_manual_acceptance_record`
- **AND** the record SHALL expose `artifact_written=true`, `covered_outcomes`, `missing_outcomes`, `execution_mode=manual_acceptance_record`, and `side_effect_level=file_write`.

#### Scenario: Recorder dry-run does not write artifact

- **GIVEN** a caller provides valid manual acceptance inputs
- **WHEN** the task runs with `dry_run=true`
- **THEN** it SHALL return the same artifact payload and metadata
- **AND** it SHALL include `artifact_written=false`
- **AND** it SHALL NOT create or overwrite the output file
- **AND** `side_effect_level` SHALL be `none`.

#### Scenario: Missing required outcomes are rejected

- **GIVEN** a caller omits one or more required outcomes
- **WHEN** the task validates the recorder request
- **THEN** it SHALL return `ErrorCode.INVALID_REQUEST`
- **AND** it SHALL list the missing outcomes
- **AND** it SHALL NOT write the artifact.

#### Scenario: Existing output path is protected by default

- **GIVEN** the output path already exists
- **WHEN** the task runs with `overwrite=false`
- **THEN** it SHALL return `ErrorCode.INVALID_REQUEST`
- **AND** it SHALL NOT overwrite the existing artifact.

### Requirement: PingAn live/manual acceptance artifacts SHALL carry recorder provenance

`TdxTaskManager.pingan_live_manual_acceptance(...)` SHALL include readiness evidence artifact provenance in generated live/manual acceptance artifacts so downstream readiness gates can distinguish controlled recorder output from hand-written JSON.

#### Scenario: Recorder writes provenance metadata

- **WHEN** the recorder writes a `tdx.desktop_trade.pingan_live_manual_acceptance.v1` artifact
- **THEN** the artifact SHALL contain `artifact_provenance.schema=tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- **AND** `artifact_provenance.source_kind` SHALL be `live_manual_acceptance`
- **AND** `artifact_provenance.producer` SHALL be `task pingan-live-manual-acceptance`
- **AND** `artifact_provenance.evidence_schema` SHALL be `tdx.desktop_trade.pingan_live_manual_acceptance.v1`.

### Requirement: PingAn acceptance coverage SHALL require verified live/manual recorder provenance

The acceptance coverage status SHALL treat live/manual acceptance as complete only when the artifact has valid outcome coverage and verified recorder provenance.

#### Scenario: Provenance-less manual acceptance artifact remains incomplete

- **GIVEN** a live/manual acceptance artifact has the expected schema and all required accepted outcomes
- **BUT** it lacks valid `artifact_provenance`
- **WHEN** acceptance coverage evaluates the artifact
- **THEN** `live_manual_acceptance.status` SHALL report `incomplete`
- **AND** `live_manual_acceptance.artifact_provenance_status.status` SHALL report `unverified`
- **AND** `live_manual_acceptance_complete` SHALL be false
- **AND** `acceptance_complete` SHALL be false.

#### Scenario: Recorder-produced manual acceptance artifact completes the gate

- **GIVEN** a live/manual acceptance artifact has the expected schema, all required accepted outcomes, and verified recorder provenance
- **WHEN** acceptance coverage evaluates the artifact
- **THEN** `live_manual_acceptance.status` SHALL report `complete`
- **AND** `live_manual_acceptance.artifact_provenance_status.status` SHALL report `verified`
- **AND** `live_manual_acceptance_complete` SHALL be true when automated outcome coverage is complete.

### Requirement: PingAn promotion readiness rollup SHALL surface live/manual recorder provenance

`TdxTaskManager.pingan_promotion_readiness_rollup(...)` SHALL include live/manual acceptance recorder provenance status in its read-only rollup and block implemented-status review when the nested recorder provenance is missing or unverified.

#### Scenario: Rollup blocks unverified live/manual recorder provenance

- **GIVEN** preflight, dialog readiness, and acceptance coverage evidence otherwise report complete gates
- **BUT** the nested live/manual acceptance artifact provenance is missing or unverified
- **WHEN** the promotion readiness rollup is built
- **THEN** `live_manual_acceptance_provenance_status.status` SHALL be `unverified`
- **AND** `gate_statuses.live_manual_acceptance.complete` SHALL be false
- **AND** `implemented_status_promotion_decision.blocked_reasons` SHALL include `unverified_live_manual_acceptance_artifact_provenance`
- **AND** the rollup SHALL remain read-only with no order submission and no FUNCTION_TREE status transition.

### Requirement: PingAn promotion readiness SHALL emit implemented-status review packet

`TdxTaskManager.pingan_promotion_readiness_rollup(...)` SHALL emit an `implemented_status_review_packet` that packages the promotion decision and evidence state into a controlled manual review input.

#### Scenario: Eligible readiness emits review packet without status transition

- **GIVEN** all required gates are complete and evidence validation has no blocking reasons
- **WHEN** the task builds `promotion_readiness_rollup`
- **THEN** the rollup SHALL include `implemented_status_review_packet`
- **AND** the packet SHALL use schema `tdx.desktop_trade.pingan_implemented_status_review_packet.v1`
- **AND** `review_status` SHALL be `ready_for_manual_review`
- **AND** `target_nodes` SHALL be `D-07` and `D-08`
- **AND** `current_function_tree_status` SHALL be `[部分实现]`
- **AND** `manual_status_review_required` SHALL be true
- **AND** `function_tree_status_transition_executed` SHALL be false
- **AND** the packet SHALL list completed gates, evidence summaries, and manual confirmation items.

#### Scenario: Blocked readiness emits blocked review packet

- **GIVEN** one or more promotion readiness blocks remain
- **WHEN** the task builds `promotion_readiness_rollup`
- **THEN** `implemented_status_review_packet.review_status` SHALL be `blocked`
- **AND** the packet SHALL include `blocked_reasons`
- **AND** the packet SHALL include incomplete gates
- **AND** the packet SHALL state that status transition is not authorized.

#### Scenario: Review packet remains read-only

- **WHEN** the task emits `implemented_status_review_packet`
- **THEN** the packet SHALL record `execution_mode=readonly_status_review_packet`
- **AND** `side_effect_level=none`
- **AND** `order_submitted=false`
- **AND** `function_tree_status_transition_executed=false`.
