# tdx-desktop-trading-management Specification

## Purpose

定义与查询 API 主线并行的桌面自动化交易管理能力，包括独立的顶层治理边界、稳定交易入口和标准化交易状态回填能力。
## Requirements
### Requirement: Desktop trading management SHALL exist as a capability parallel to query API management
The system SHALL define desktop automation trading as an independent capability instead of treating it as an extension of query API management.

#### Scenario: Project architecture distinguishes query and trading governance
- **WHEN** the project documents or code structure describe top-level capabilities
- **THEN** desktop automation trading MUST be represented as a capability parallel to `tdx-api-management`

#### Scenario: Desktop trading is not attached to TdxApiManager
- **WHEN** a caller needs to execute desktop automation trading behavior
- **THEN** that behavior MUST NOT be modeled as a method added onto `TdxApiManager`

### Requirement: Desktop trading management SHALL preserve existing production trading flows during capability separation
The system SHALL keep the current production desktop trading flows usable while the capability boundary is formalized.

#### Scenario: Existing flat trading commands remain usable
- **WHEN** the desktop trading capability is formally introduced
- **THEN** existing commands such as `pingan-buy-submit-once` and `pingan-buy` MUST remain available during the migration period

#### Scenario: Existing desktop modules remain valid implementation anchors
- **WHEN** the capability boundary is documented
- **THEN** the current `tdxquant/desktop/`, `tdxquant/brokers/`, and related runtime/CLI paths MUST remain valid implementation anchors rather than being deprecated immediately

### Requirement: Desktop trading management SHALL define a dedicated top-level management path
The system SHALL reserve a dedicated top-level management path for desktop automation trading instead of routing it through query API management.

#### Scenario: Future top-level trade manager is introduced
- **WHEN** the project introduces a standardized top-level desktop trading entrypoint
- **THEN** it MUST be introduced as a dedicated trade management surface such as `TradeManager` or an equivalent trading facade

#### Scenario: Trading governance remains distinct from read-only query governance
- **WHEN** top-level management behavior is designed
- **THEN** trading-specific concerns such as window state, HID/Win32/UIA coordination, confirmation handling, and state backfill MUST remain governed by the desktop trading management capability

#### Scenario: Caller uses TradeManager for Ping An buy workflow
- **WHEN** a caller executes the stable Ping An desktop buy workflow through the top-level management layer
- **THEN** the system MUST expose that workflow through a dedicated trade manager path rather than direct attachment to `TdxApiManager`

#### Scenario: TradeManager persists trading artifacts after execution
- **WHEN** a top-level desktop trading workflow completes
- **THEN** the trading management layer MUST be able to write standardized state backfill artifacts such as last-order state or append-only event logs

### Requirement: Desktop trading management SHALL preserve trade safety context in persisted artifacts
The system SHALL persist normalized trade safety context into the existing last-order state and append-only event artifacts for stable desktop trading workflows.

#### Scenario: Trade manager writes safety-aware artifacts
- **WHEN** a stable desktop trade workflow finishes through `TdxTradeManager`
- **THEN** the written last-order state payload and append-only event row MUST include the normalized trade safety summary

### Requirement: Desktop trading management SHALL accept caller safety controls for stable buy workflows
The system SHALL allow stable desktop buy workflows to accept caller safety controls without breaking existing production trade flows.

#### Scenario: Caller supplies safety controls to stable desktop buy workflow
- **WHEN** a caller executes a stable desktop buy workflow through the top-level trade manager and supplies `submission_key` or `max_price`
- **THEN** the workflow MUST accept those options
- **AND** existing required trade inputs and production flow behavior MUST remain unchanged

### Requirement: Desktop trading management SHALL expose submission-ledger artifacts for keyed stable workflows
The system SHALL expose the durable submission-ledger artifact path for keyed stable desktop trade workflows.

#### Scenario: Keyed trade result exposes ledger artifact path
- **WHEN** a keyed stable desktop trade workflow finishes through `TdxTradeManager`
- **THEN** the result artifacts MUST expose the durable submission-ledger path

### Requirement: Desktop trading management SHALL consult the submission ledger before stable desktop execution
The system SHALL consult the durable submission ledger before executing a keyed stable desktop trade workflow.

#### Scenario: Submission ledger prevents duplicate desktop execution
- **WHEN** a keyed stable desktop trade workflow is invoked
- **THEN** the management layer MUST consult the current submission ledger before desktop execution
- **AND** the management layer MUST apply duplicate-short-circuit or conflicting-key rejection behavior when the ledger requires it

### Requirement: Desktop trading management SHALL expose trade-audit target discovery together with existing artifact governance
The system SHALL expose the configured trade-audit artifact target alongside the existing state, event-log, and submission-ledger artifact targets.

#### Scenario: Trade readiness summary includes trade-audit target
- **WHEN** a caller executes a stable trade discovery-style workflow such as health, preflight, or dialog readiness
- **THEN** the returned artifact target summary MUST include the configured trade-audit target path in addition to the existing trade artifact targets

### Requirement: Desktop trading management SHALL preserve audit correlation in persisted artifacts
The system SHALL preserve normalized trade-audit correlation data across the existing state and event artifacts for finalized stable trade workflows.

#### Scenario: Finalized trade writes audit-aware persisted artifacts
- **WHEN** a stable desktop trade workflow finishes through the finalized persistence path
- **THEN** the written last-order state payload MUST include the normalized `trade_audit` summary
- **AND** the appended order-event row MUST include the normalized `trade_audit` summary

### Requirement: Desktop trading management SHALL expose a dedicated Ping An sell submit-once identity

The desktop trading management layer SHALL expose a dedicated Ping An sell submit-once manager path that preserves existing sell execution behavior while recording submit-once-specific identity.

#### Scenario: Caller runs Ping An sell submit-once through the trade manager

- **WHEN** a caller executes `TdxTradeManager.pingan.sell_submit_once`
- **THEN** the manager MUST reuse the existing Ping An sell desktop execution flow
- **AND** the result metadata MUST record the manager method as `sell_submit_once`
- **AND** idempotency and safety controls such as `submission_key` and `max_price` MUST continue to apply before desktop execution

#### Scenario: Caller inspects sell submit-once boundaries

- **WHEN** a caller uses the dedicated sell submit-once manager path
- **THEN** the system MUST NOT imply a separate `run_pingan_sell_submit_once` desktop primitive exists
- **AND** the boundary MUST remain limited to the existing Ping An sell desktop workflow

### Requirement: Desktop trading management SHALL expose explicit PingAn lifecycle owner lock control

The PingAn desktop trading management layer SHALL expose a deterministic local lifecycle owner lock surface that can inspect, acquire, and release ownership without controlling the real desktop process.

#### Scenario: Caller inspects lifecycle owner lock status

- **WHEN** a caller requests PingAn lifecycle owner lock `status` with a statefile path and owner token
- **THEN** the manager SHALL return a successful read-only payload
- **AND** the payload SHALL include the requested action, statefile path, lock path, owner token, stale detection fields, and `statefile_write_executed=false`.

#### Scenario: Caller acquires lifecycle owner lock

- **WHEN** a caller requests PingAn lifecycle owner lock `acquire` with a statefile path and owner token
- **THEN** the manager SHALL create the parent directory when needed
- **AND** the manager SHALL write a sibling lock file and lifecycle statefile recording `status=owned`
- **AND** the result payload SHALL report `lock_acquired=true`, `statefile_write_executed=true`, and the owner token.

#### Scenario: Caller releases lifecycle owner lock

- **WHEN** a caller requests PingAn lifecycle owner lock `release` with the same owner token recorded in the statefile
- **THEN** the manager SHALL remove the sibling lock file when present
- **AND** the manager SHALL write a lifecycle statefile recording `status=released`
- **AND** the result payload SHALL report `lock_released=true` and `statefile_write_executed=true`.

#### Scenario: Caller does not own an active lifecycle lock

- **WHEN** a caller attempts to acquire a non-stale lock owned by another owner token
- **THEN** the manager SHALL reject the request without overwriting the statefile or lock file
- **AND** the payload SHALL report the blocking owner token, stale status, and `statefile_write_executed=false`.

#### Scenario: Caller handles stale lifecycle lock explicitly

- **WHEN** a caller attempts to acquire a stale lock
- **THEN** the manager SHALL report stale status
- **AND** the manager SHALL replace the stale lock only when the caller explicitly enables stale replacement.

### Requirement: Desktop trading management SHALL validate PingAn lifecycle owner PID liveness

The PingAn lifecycle owner lock payload SHALL include local owner PID liveness diagnostics when owner state is available.

#### Scenario: Caller checks owner lock status with alive owner PID

- **WHEN** a caller requests PingAn lifecycle owner lock `status` for a statefile that records an alive owner PID
- **THEN** the payload SHALL include `pid_validation_executed=true`
- **AND** the payload SHALL include the recorded `owner_pid`, `owner_pid_alive=true`, and `owner_pid_status=alive`.

#### Scenario: Caller checks owner lock status with missing owner PID

- **WHEN** a caller requests PingAn lifecycle owner lock `status` for a statefile without a valid owner PID
- **THEN** the payload SHALL include `pid_validation_executed=true`
- **AND** the payload SHALL include `owner_pid=null`, `owner_pid_alive=null`, and `owner_pid_status=missing`.

#### Scenario: Acquire and release expose owner PID diagnostics

- **WHEN** a caller acquires or releases a PingAn lifecycle owner lock
- **THEN** the returned payload SHALL include owner PID validation fields
- **AND** the payload SHALL keep `pid_ownership_claimed=false`.

### Requirement: Desktop trading management SHALL expose PingAn lifecycle supervisor control

Desktop trading management SHALL expose explicit PingAn lifecycle supervisor tick and bounded foreground run operations that are guarded by the existing local lifecycle owner lock before recording restart/backoff decisions.

#### Scenario: Supervisor tick rejects unowned lifecycle state without control side effects

- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_tick` without an owned local lifecycle statefile for the provided owner token
- **THEN** the result MUST report `supervisor_owned=false`
- **AND** the result MUST report `control_dispatch_executed=false`
- **AND** the result MUST report `restart_executed=false`
- **AND** the result MUST report `backoff_executed=false`
- **AND** the result MUST NOT call broker health observation.

#### Scenario: Supervisor tick records restart and backoff decisions under ownership

- **GIVEN** a caller has acquired the local PingAn lifecycle owner lock for the provided owner token
- **WHEN** `TdxTradeManager.pingan.lifecycle_supervisor_tick` observes unhealthy broker health
- **THEN** the first eligible tick MUST write a local lifecycle statefile supervisor update with `restart_executed=true`
- **AND** a later tick inside the configured backoff window MUST write a local lifecycle statefile supervisor update with `backoff_executed=true`
- **AND** both updates MUST report `order_submitted=false`, `process_kill_executed=false`, and `pid_ownership_claimed=false`.

#### Scenario: Supervisor run bounds the number of control ticks

- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_run` with `max_ticks=N`
- **THEN** the operation MUST execute no more than `N` supervisor ticks
- **AND** the returned summary MUST include the observed tick count and per-tick results.

### Requirement: Desktop trading management SHALL expose explicit PingAn process lifecycle control

Desktop trading management SHALL expose explicit local PingAn process lifecycle status/start/stop/restart operations that are guarded by the existing lifecycle owner lock and constrained to the process PID recorded in the lifecycle statefile.

#### Scenario: Mutating process lifecycle actions reject missing owner lock

- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_process(action=start|stop|restart)` without a matching owned lifecycle owner lock
- **THEN** the result MUST be rejected
- **AND** the result MUST report `process_start_executed=false`
- **AND** the result MUST report `process_stop_executed=false`
- **AND** the result MUST report `process_kill_executed=false`
- **AND** the result MUST NOT spawn or terminate a process.

#### Scenario: Start records an owned process PID

- **GIVEN** a caller has acquired the local PingAn lifecycle owner lock
- **WHEN** the caller invokes `TdxTradeManager.pingan.lifecycle_process(action=start, exe_path=<path>)`
- **THEN** the manager MUST start the executable through a bounded subprocess call
- **AND** the manager MUST write the spawned PID, command, owner token, and start timestamp to the lifecycle statefile
- **AND** the result MUST report `pid_ownership_claimed=true` for that spawned process.

#### Scenario: Stop only targets the recorded owned PID

- **GIVEN** the lifecycle statefile contains a process PID recorded by the same owner token and command
- **WHEN** the caller invokes `TdxTradeManager.pingan.lifecycle_process(action=stop)`
- **THEN** the manager MUST terminate only the recorded PID
- **AND** the manager MUST write stop evidence to the lifecycle statefile
- **AND** the result MUST NOT claim broad PingAn process discovery or unrelated PID ownership.

#### Scenario: Restart is composed from guarded recorded PID stop and start

- **GIVEN** the lifecycle statefile contains a process PID recorded by the same owner token and command
- **WHEN** the caller invokes `TdxTradeManager.pingan.lifecycle_process(action=restart)`
- **THEN** the manager MUST record a restart operation using the same recorded-PID guard as stop
- **AND** the manager MUST write the newly spawned PID to the lifecycle statefile.

### Requirement: PingAn lifecycle supervisor SHALL optionally execute recorded-PID process restart

PingAn lifecycle supervisor tick/run SHALL optionally execute the existing recorded-PID guarded process restart when the supervisor restart/backoff policy allows a restart and the caller explicitly opts in.

#### Scenario: Eligible supervisor restart executes recorded-PID process restart when opted in

- **GIVEN** the lifecycle owner lock is owned by the caller
- **AND** the lifecycle statefile contains a process PID recorded by the same owner token and command
- **AND** broker health is unhealthy
- **AND** restart/backoff policy allows a restart attempt
- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_tick(process_restart_enabled=true)`
- **THEN** the supervisor MUST call the existing `lifecycle_process(action=restart)` path
- **AND** the supervisor payload MUST report `process_restart_requested=true`
- **AND** the supervisor payload MUST report `process_restart_executed=true` when the recorded-PID restart succeeds
- **AND** the supervisor payload MUST include the process restart result summary.

#### Scenario: Backoff prevents process restart even when opt-in is enabled

- **GIVEN** a prior supervisor restart attempt is still inside the configured backoff window
- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_tick(process_restart_enabled=true)`
- **THEN** the supervisor MUST report `backoff_executed=true`
- **AND** the supervisor MUST report `process_restart_requested=false`
- **AND** the supervisor MUST NOT call process lifecycle restart.

#### Scenario: Default supervisor restart remains statefile-only

- **WHEN** a supervisor restart is eligible but `process_restart_enabled=false`
- **THEN** the supervisor MUST preserve the existing statefile-backed restart decision behavior
- **AND** it MUST report `process_restart_requested=false`
- **AND** it MUST NOT call process lifecycle restart.

### Requirement: PingAn lifecycle supervisor SHALL summarize post-restart broker health

PingAn lifecycle supervisor tick/run SHALL optionally perform one bounded broker health recheck after a successful recorded-PID process restart and expose a recovery summary.

#### Scenario: Successful restart recheck reports recovered lifecycle status

- **GIVEN** supervisor process restart is explicitly enabled
- **AND** the recorded-PID process restart succeeds
- **AND** restart recheck is explicitly enabled
- **WHEN** the post-restart broker health check returns OK
- **THEN** the supervisor payload MUST report `process_restart_recheck_requested=true`
- **AND** the supervisor payload MUST report `process_restart_recheck_executed=true`
- **AND** the supervisor payload MUST report `post_restart_broker_health_ok=true`
- **AND** the supervisor payload MUST report `lifecycle_recovery_status=recovered`.

#### Scenario: Failed restart recheck reports still unhealthy without failing restart evidence

- **GIVEN** supervisor process restart succeeds
- **AND** restart recheck is explicitly enabled
- **WHEN** the post-restart broker health check returns non-OK
- **THEN** the supervisor payload MUST report `process_restart_executed=true`
- **AND** the supervisor payload MUST report `post_restart_broker_health_ok=false`
- **AND** the supervisor payload MUST report `lifecycle_recovery_status=still_unhealthy`
- **AND** the supervisor result MUST remain structured lifecycle evidence rather than submitting or retrying an order.

#### Scenario: Recheck remains absent when restart is not executed

- **WHEN** supervisor is inside backoff, max restart attempts are exhausted, process restart is disabled, or process restart fails
- **THEN** the supervisor payload MUST report `process_restart_recheck_requested=false`
- **AND** the supervisor payload MUST report `process_restart_recheck_executed=false`.

### Requirement: PingAn lifecycle supervisor SHALL expose a controller boundary for safety gate and restart policy decisions
The PingAn desktop trading lifecycle supervisor SHALL isolate owner-lock gate evaluation and restart/backoff policy decisions behind an explicit lifecycle controller boundary while preserving the existing trade manager public lifecycle methods.

#### Scenario: Controller rejects supervisor tick without owner side effects
- **WHEN** the lifecycle controller evaluates a supervisor tick whose owner-lock status is not owned by the requested owner token
- **THEN** it MUST return a structured owner-gate rejection payload with `supervisor_owned=false`
- **AND** it MUST report `control_dispatch_executed=false`, `restart_executed=false`, `backoff_executed=false`, `statefile_write_executed=false`, `order_submitted=false`, `process_kill_executed=false`, and `pid_ownership_claimed=false`

#### Scenario: Controller decides restart and backoff without executing process control
- **WHEN** the lifecycle controller evaluates unhealthy broker state under an owned supervisor state
- **THEN** it MUST identify the first eligible restart decision and subsequent backoff decision from prior supervisor state
- **AND** the controller decision MUST NOT execute process start, stop, kill, order submission, or desktop automation

#### Scenario: Public supervisor tick preserves existing lifecycle behavior
- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_tick`
- **THEN** the public result shape and safety fields MUST remain compatible with the existing lifecycle supervisor contract
- **AND** actual process restart MUST remain opt-in and delegated to the existing recorded-PID guarded lifecycle process path

### Requirement: PingAn process lifecycle SHALL expose a controller boundary for owner and recorded-PID guard decisions

The PingAn desktop trading process lifecycle path SHALL isolate owner-lock gate evaluation, process result-shape construction, and recorded-PID guard decisions behind an explicit lifecycle controller boundary while preserving the existing public process lifecycle behavior.

#### Scenario: Controller rejects process owner gate without process side effects

- **WHEN** the lifecycle controller evaluates a process lifecycle owner gate whose owner-lock status is not owned by the requested owner token
- **THEN** it MUST return a structured owner-gate rejection decision with `owner_ok=false`
- **AND** its rejection payload MUST report `process_start_executed=false`, `process_stop_executed=false`, `process_kill_executed=false`, `statefile_write_executed=false`, `order_submitted=false`, and `pid_ownership_claimed=false`
- **AND** the controller MUST NOT spawn, stop, kill, automate, or submit anything.

#### Scenario: Controller rejects recorded-PID guard without process side effects

- **WHEN** the lifecycle controller evaluates a stop or restart action without a usable recorded process PID, matching owner token, or matching command ownership
- **THEN** it MUST return a structured guard rejection result
- **AND** the result MUST report `process_start_executed=false`, `process_stop_executed=false`, `process_kill_executed=false`, `statefile_write_executed=false`, `order_submitted=false`, and `pid_ownership_claimed=false`
- **AND** the controller MUST NOT call process kill, process spawn, statefile write, desktop automation, or order submission.

#### Scenario: Public process lifecycle behavior remains stable

- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_process(...)`
- **THEN** the public result shape and side-effect flags MUST remain compatible with the existing process lifecycle contract
- **AND** real process start/stop/restart execution MUST remain explicit, owner-gated, and constrained to the existing recorded-PID guarded manager path.

### Requirement: PingAn trade management SHALL expose read-only execution acceptance evidence

PingAn desktop trading management SHALL expose a read-only acceptance evidence summary for the implemented D-07 and D-08 trade execution surface.

#### Scenario: Acceptance evidence summary covers implemented trade surfaces without execution

- **WHEN** a caller requests PingAn trade execution acceptance evidence
- **THEN** the result MUST identify target nodes `D-07` and `D-08`
- **AND** it MUST enumerate the covered buy, sell, confirm-current, and submit-once trade surfaces
- **AND** it MUST expose explicit false side-effect flags for trade dispatch, order submission, workflow dispatch, desktop automation, process control, and status transition.

#### Scenario: Acceptance evidence summary remains a bounded review aid

- **WHEN** the acceptance evidence summary is returned
- **THEN** the payload MUST state that it is read-only evidence for manual/operator review
- **AND** it MUST NOT claim broker readiness, production readiness, live/manual acceptance completion, or automatic FUNCTION_TREE status transition.

### Requirement: Desktop trading management SHALL route PingAn order execution through an internal execution seam
The desktop trading management layer SHALL provide an internal PingAn order execution seam that accepts a normalized order request, preserves public method identity, applies caller-provided gate decisions before desktop dispatch, and returns the existing manager result shape. The public `TdxTradeManager.pingan.*` methods MUST remain the supported caller interface.

#### Scenario: Buy submit-once uses the internal execution seam
- **WHEN** a caller executes `TdxTradeManager.pingan.buy_submit_once(...)`
- **THEN** the manager MUST route the normalized buy submit-once request through the internal PingAn execution seam before desktop dispatch
- **AND** the public result MUST preserve existing audit, idempotency, safety, lifecycle, and artifact fields

#### Scenario: Rejected gate stops before desktop dispatch
- **WHEN** a normalized PingAn execution request has a failed idempotency, safety, lifecycle owner, or broker-readiness gate
- **THEN** the internal execution seam MUST return the existing rejected manager result shape without invoking the desktop dispatch callback

#### Scenario: Public contract remains stable
- **WHEN** callers use existing PingAn manager, CLI, task, or catalog entry points
- **THEN** no new public parameter, command, catalog entry, desktop primitive, or live execution guarantee is introduced by the internal module extraction

### Requirement: Desktop trading management SHALL align PingAn submit-once sides behind the internal execution seam
The desktop trading management layer SHALL route both PingAn buy submit-once and sell submit-once manager paths through the internal PingAn execution seam while preserving public manager contracts, method identity, safety gates, lifecycle/broker readiness gates, audit metadata, and artifact behavior.

#### Scenario: Sell submit-once uses the internal execution seam
- **WHEN** a caller executes `TdxTradeManager.pingan.sell_submit_once(...)`
- **THEN** the manager MUST route the normalized sell submit-once request through the internal PingAn execution seam before desktop dispatch
- **AND** the public result MUST preserve existing `method=sell_submit_once` manager/audit identity and safety metadata

#### Scenario: Sell submit-once desktop primitive boundary is preserved
- **WHEN** the internal execution seam dispatches a sell submit-once request
- **THEN** the desktop dispatch MUST continue to use the existing sell desktop flow
- **AND** the system MUST NOT imply that a separate `run_pingan_sell_submit_once` desktop primitive exists

