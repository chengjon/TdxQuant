# tdx-desktop-trading-safety Specification

## Purpose

定义稳定桌面交易结果中的安全治理契约，包括风险门、submission key 和 idempotency 摘要。
## Requirements
### Requirement: Stable desktop trade workflows SHALL expose normalized trade safety metadata
The system SHALL attach a stable `trade_safety` object to stable desktop trade workflow results so callers can reason about operational risk without parsing free-form messages.

#### Scenario: Successful trade returns normalized safety metadata
- **WHEN** a caller executes a stable desktop trade workflow through `TdxTradeManager`
- **THEN** the result `data` MUST include `trade_safety`
- **AND** `trade_safety` MUST include a stability grade, side-effect grade, submission-key field, risk-gate summary, and idempotency summary

### Requirement: Stable desktop trade workflows SHALL preserve an optional submission key
The system SHALL preserve an optional caller-supplied `submission_key` across result payloads and persisted trade artifacts.

#### Scenario: Caller provides submission key
- **WHEN** a caller executes a stable desktop trade workflow with a `submission_key`
- **THEN** the result `data.trade_safety.submission_key` MUST equal the caller value
- **AND** the persisted last-order state payload and append-only event row MUST contain the same key

### Requirement: Stable desktop trade workflows SHALL reject failed pre-trade risk gates before UI side effects
The system SHALL reject invalid requests before any desktop automation side effects execute.

#### Scenario: Invalid order request fails before desktop execution
- **WHEN** a caller submits an invalid stable desktop order request
- **THEN** the workflow MUST return an invalid-request style result
- **AND** the desktop execution routine MUST NOT be called

#### Scenario: Submitted price exceeds caller ceiling
- **WHEN** a caller supplies `max_price` and the requested order price is greater than that ceiling
- **THEN** the workflow MUST return an invalid-request style result
- **AND** the desktop execution routine MUST NOT be called

### Requirement: PingAn live trading implementation SHALL be gated by safety and acceptance evidence

D-07 and D-08 SHALL remain `[部分实现]` until implementation evidence covers all ordered promotion gates. Readonly provider/broker ownership plus safety preflight status, readonly desktop dialog lifecycle status, per-result audit gate status, read-only acceptance outcome coverage status, and failed audit classification status SHALL count only as partial promotion evidence and SHALL NOT by themselves satisfy live trading implementation.

#### Scenario: Live trading promotion requires ordered gates

- **WHEN** a later change attempts to promote D-07 or D-08 to `[已实现]`
- **THEN** the change MUST provide provider/broker ownership evidence
- **AND** safety evidence for max price or equivalent guardrails, submission-key/idempotency, and explicit approval semantics
- **AND** desktop lifecycle evidence for dialog readiness, result popups, exception popups, timeout/retry handling, and process/window ownership
- **AND** audit evidence for success/failure/rejection/exception paths
- **AND** automated fake/replay verification plus documented manual/live acceptance evidence where the real environment is required.

#### Scenario: Read-only catalog evidence cannot satisfy live trading safety gates

- **WHEN** D-07 or D-08 evidence only shows catalog validation, catalog plan, catalog preview, or bundle summary output
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that catalog-only evidence is non-executing discovery evidence and does not prove broker readiness, approval safety, desktop lifecycle coverage, audit coverage, or production readiness.

#### Scenario: Read-only preflight evidence remains partial

- **WHEN** D-07 or D-08 evidence includes PingAn provider/broker ownership and safety gate status from readonly preflight
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that lifecycle, audit, and acceptance gates still remain before `[已实现]`.

#### Scenario: Read-only dialog lifecycle evidence remains partial

- **WHEN** D-07 or D-08 evidence includes PingAn desktop lifecycle gate status from readonly dialog readiness
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that exception popup handling, retry policy, audit evidence, and acceptance evidence still remain before `[已实现]`.

#### Scenario: Per-result audit evidence remains partial

- **WHEN** D-07 or D-08 evidence includes PingAn `trade_audit_gate_status` from finalized trade results
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that all required outcome statuses, exception handling, and acceptance evidence still remain before `[已实现]`.

#### Scenario: Explicit exception audit evidence remains partial

- **WHEN** D-07 or D-08 evidence includes PingAn `trade_audit_gate_status.covered_audit_status=exception` from an explicitly exception-marked finalized result
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that this classifies explicit exception metadata only and does not prove exception popup handling, retry policy, or live/manual acceptance.

#### Scenario: Failed audit classification evidence remains partial

- **WHEN** D-07 or D-08 evidence includes PingAn `trade_audit_gate_status.audit_status_classification.source=generic_execution_failure`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that this classifies a finalized generic failed outcome only and does not prove retry, recovery, broker readiness, or live/manual acceptance.

#### Scenario: Read-only acceptance outcome coverage evidence remains partial

- **WHEN** D-07 or D-08 evidence includes PingAn `acceptance_outcome_coverage_status` from trade audit reports
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the payload is read-only report evidence
- **AND** the boundary MUST separately list missing automated outcome statuses and missing live/manual acceptance evidence before `[已实现]`.

### Requirement: PingAn preflight SHALL expose provider and safety promotion gate status

The PingAn desktop trade preflight SHALL expose a readonly `promotion_gate_status` payload that summarizes provider/broker ownership and safety readiness without submitting an order.

#### Scenario: Preflight reports broker ownership and non-execution boundary

- **WHEN** `TdxTradeManager.pingan.preflight` completes
- **THEN** the result data SHALL include `promotion_gate_status.provider_broker_ownership`
- **AND** that provider/broker ownership payload SHALL identify `broker=pingan_desktop`, the PingAn desktop adapter/manager ownership, supported brokers, `execution_mode=readonly_preflight`, `dispatch_executed=false`, and `order_submitted=false`.

#### Scenario: Preflight reports safety gate readiness

- **WHEN** `TdxTradeManager.pingan.preflight` is called with trade inputs, `max_price`, and `submission_key`
- **THEN** the result data SHALL include `promotion_gate_status.safety_gates`
- **AND** the safety gate payload SHALL report max-price guard configuration, submission-key presence, idempotency decision, risk-gate pass/fail, explicit approval status, and remaining gate names.

#### Scenario: Preflight gate status does not satisfy implemented status by itself

- **WHEN** `promotion_gate_status` is available from preflight
- **THEN** the payload SHALL state that it is partial promotion evidence
- **AND** the remaining gates SHALL include desktop lifecycle, audit evidence, and acceptance evidence.

### Requirement: PingAn automated outcome coverage completion SHALL remain distinct from live acceptance

PingAn trade audit report coverage SHALL distinguish automated outcome coverage completion from live/manual acceptance completion.

#### Scenario: Automated outcome coverage alone remains partial

- **WHEN** D-07 or D-08 evidence includes `acceptance_outcome_coverage_status.automated_outcome_coverage_complete=true`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that live/manual acceptance, broker readiness, retry/recovery, and production readiness are not proven by automated report coverage alone.

### Requirement: PingAn passive exception popup lookup SHALL remain partial lifecycle evidence

PingAn passive exception popup lookup SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy exception popup handling, retry, recovery, or live acceptance gates.

#### Scenario: Passive exception popup lookup is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.dialog_checks.exception_popup_lookup`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the lookup does not close popups, retry orders, recover state, prove broker readiness, or provide live/manual acceptance.

### Requirement: PingAn passive process/window ownership observation SHALL remain partial lifecycle evidence

PingAn passive process/window ownership observation SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy process ownership, statefile ownership, supervisor, restart/backoff, or live acceptance gates.

#### Scenario: Passive process/window observation is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.observed_process_window_ownership`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the observation does not start, stop, restart, supervise, lock, or otherwise own the PingAn desktop process.

### Requirement: PingAn retry policy status SHALL remain partial lifecycle evidence

PingAn retry policy status SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy retry, backoff, recovery, resubmission, or live acceptance gates.

#### Scenario: Retry policy status is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.retry_policy_status`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the status does not retry, back off, recover, resubmit, or provide live/manual acceptance.

### Requirement: PingAn exception popup handling status SHALL remain partial lifecycle evidence

PingAn exception popup handling status SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy popup close, confirm click, recovery, retry, resubmission, or live acceptance gates.

#### Scenario: Exception popup handling status is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.exception_popup_handling_status`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the status does not close popups, click controls, recover, retry, resubmit, or provide live/manual acceptance.

### Requirement: PingAn statefile lock status SHALL remain partial lifecycle evidence

PingAn statefile lock status SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy statefile ownership, lock ownership, process ownership, supervisor, restart/backoff, or live acceptance gates.

#### Scenario: Statefile lock status is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.statefile_lock_status`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the status does not acquire locks, write owner tokens, write state/ledger/audit artifacts, own processes, or provide live/manual acceptance.

### Requirement: PingAn lifecycle control status SHALL remain partial lifecycle evidence

PingAn lifecycle control status SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy process lifecycle ownership, supervisor ownership, restart/backoff, statefile ownership, or live acceptance gates.

#### Scenario: Lifecycle control status is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.lifecycle_control_status`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the status does not start, stop, restart, kill, supervise, back off, claim PID ownership, write state/ledger/audit artifacts, or provide live/manual acceptance.

### Requirement: PingAn lifecycle owner lock SHALL remain statefile-only lifecycle evidence

The PingAn lifecycle owner lock surface SHALL be treated as a local ownership artifact, not as proof of executable desktop lifecycle control or live trading readiness.

#### Scenario: Lifecycle owner lock does not control desktop process

- **WHEN** PingAn lifecycle owner lock status, acquire, or release returns a payload
- **THEN** the payload MUST state that no order was submitted and no desktop control dispatch was executed
- **AND** the payload MUST state that start, stop, restart, kill, supervisor ownership, backoff execution, PID ownership, event-log writes, submission-ledger writes, and trade-audit writes were not performed.

#### Scenario: Lifecycle owner lock is registered without implemented trading status

- **WHEN** D-07 or D-08 evidence includes PingAn lifecycle owner lock acquire/release behavior
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that real process lifecycle control, supervisor ownership, restart/backoff, live provider readiness, and live/manual acceptance remain required before `[已实现]`.

### Requirement: PingAn owner PID validation SHALL NOT imply desktop process ownership

PingAn lifecycle owner PID validation SHALL remain a local diagnostic for the owner lock statefile and SHALL NOT be treated as proof of real desktop process lifecycle ownership.

#### Scenario: Owner PID validation reports alive local process

- **WHEN** PingAn lifecycle owner lock payload reports `owner_pid_alive=true`
- **THEN** the payload MUST still report `pid_ownership_claimed=false`
- **AND** it MUST still report that no start, stop, restart, kill, supervisor ownership, backoff execution, order submission, or trade artifact write occurred.

#### Scenario: Owner PID validation is registered without implemented trading status

- **WHEN** D-07 or D-08 evidence includes PingAn owner PID validation
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that owner PID liveness is only a local statefile diagnostic, not real PingAn desktop process ownership or live/manual acceptance.

### Requirement: PingAn lifecycle owner lock CLI SHALL remain partial lifecycle evidence

The PingAn lifecycle owner lock CLI entry SHALL be treated as explicit local statefile control and SHALL NOT be treated as proof of live trading readiness.

#### Scenario: Lifecycle owner lock CLI is registered without implemented trading status

- **WHEN** D-07 or D-08 evidence includes the `trade lifecycle-owner-lock` CLI entry
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the CLI writes only local owner lock state when requested and does not start, stop, restart, kill, supervise, back off, submit orders, claim real desktop PID ownership, or provide live/manual acceptance.

### Requirement: PingAn preflight owner lock status SHALL NOT imply live lifecycle readiness

PingAn lifecycle owner lock status inside preflight SHALL be treated as local read-only lifecycle evidence and SHALL NOT be treated as proof of live trading readiness or real desktop process ownership.

#### Scenario: Preflight owner lock status remains bounded

- **WHEN** PingAn preflight reports `promotion_gate_status.lifecycle_owner_lock_status`
- **THEN** the summary MUST report `pid_ownership_claimed=false`
- **AND** it MUST report that no start, stop, restart, kill, supervisor ownership, backoff execution, owner lock acquire/release, order submission, or trade artifact write occurred.

#### Scenario: Preflight owner lock status is registered without implemented trading status

- **WHEN** D-07 or D-08 evidence includes the PingAn preflight lifecycle owner lock status gate
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that preflight owner lock status is a local statefile diagnostic and does not provide real process lifecycle control, broker readiness, or live/manual acceptance.

### Requirement: PingAn required owner lock preflight gate SHALL remain local safety evidence

PingAn required owner lock preflight behavior SHALL be treated as local statefile safety evidence and SHALL NOT be treated as proof of live trading readiness, broker readiness, or real process ownership.

#### Scenario: Required owner lock gate remains bounded

- **WHEN** PingAn preflight reports `lifecycle_owner_lock_status.required=true`
- **THEN** the summary MUST still report `pid_ownership_claimed=false`
- **AND** it MUST report that no lifecycle control, owner lock acquire/release, order submission, or trade artifact write occurred.

#### Scenario: Required owner lock gate is registered without implemented trading status

- **WHEN** D-07 or D-08 evidence includes the required owner lock preflight gate
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that this gate is only a local preflight safety check and does not provide broker readiness or live/manual acceptance.

### Requirement: PingAn execution SHALL optionally require local lifecycle owner lock ownership

Side-effecting PingAn desktop trade execution methods SHALL support an opt-in local lifecycle owner-lock requirement that is evaluated before desktop automation dispatch.

#### Scenario: Required owner lock blocks buy execution before desktop dispatch

- **WHEN** a caller executes PingAn buy with `require_lifecycle_owner_lock=true`
- **AND** the local lifecycle owner lock is missing, stale, released, unknown, or held by another owner token
- **THEN** the result MUST be rejected before desktop automation dispatch
- **AND** `trade_safety.risk_gate.lifecycle_owner_lock_required_status` MUST report `requirement_status=failed`
- **AND** the guard MUST NOT acquire or release owner locks.

#### Scenario: Required owner lock allows execution when owned by caller token

- **WHEN** a caller executes PingAn buy, sell, buy-submit-once, or sell-submit-once with `require_lifecycle_owner_lock=true`
- **AND** the local lifecycle owner lock is `owned`, non-stale, and owned by the caller token
- **THEN** the guard MUST report `requirement_status=passed`
- **AND** the desktop execution path MAY proceed to the existing risk/idempotency and desktop automation flow.

### Requirement: PingAn execution owner-lock guard SHALL remain local safety evidence

The PingAn execution owner-lock guard SHALL remain a local statefile safety guard and SHALL NOT imply real process lifecycle control.

#### Scenario: Execution guard remains bounded

- **WHEN** PingAn execution reports `lifecycle_owner_lock_required_status`
- **THEN** the status MUST report `pid_ownership_claimed=false`
- **AND** it MUST report no start, stop, restart, kill, supervisor ownership, backoff execution, owner lock acquire/release, or lifecycle statefile write from the guard itself.

### Requirement: PingAn confirm-current SHALL honor lifecycle owner-lock guard
PingAn confirm-current execution SHALL accept optional lifecycle owner-lock guard options and MUST reject before advancing the current confirmation dialog when the guard is explicitly required and not satisfied.

#### Scenario: Confirm-current rejects before dialog advancement when owner lock is required but unavailable
- **WHEN** `TdxTradeManager.pingan.confirm_current(...)` is called with `require_lifecycle_owner_lock=true` and no valid owner-lock status can satisfy the requirement
- **THEN** the manager MUST return a failed result containing `lifecycle_owner_lock_required_status`
- **AND** the manager MUST NOT run confirm dialog lookup or click behavior

#### Scenario: Confirm-current keeps default behavior when owner lock is not required
- **WHEN** `TdxTradeManager.pingan.confirm_current(...)` is called without lifecycle owner-lock guard options
- **THEN** the manager MUST preserve the existing confirm-current dialog boundary workflow
- **AND** the manager MUST NOT require lifecycle statefile ownership.

### Requirement: PingAn submit-ready SHALL honor lifecycle owner-lock guard
PingAn submit-ready execution SHALL accept optional lifecycle owner-lock guard options and MUST reject before running the HID submit probe when the guard is explicitly required and not satisfied.

#### Scenario: Submit-ready rejects before HID submit probe when owner lock is required but unavailable
- **WHEN** `TdxTradeManager.pingan.submit_ready(...)` is called with `require_lifecycle_owner_lock=true` and no valid owner-lock status can satisfy the requirement
- **THEN** the manager MUST return a failed result containing `lifecycle_owner_lock_required_status`
- **AND** the manager MUST NOT run HID submit probe or confirm dialog lookup behavior.

#### Scenario: Submit-ready keeps default behavior when owner lock is not required
- **WHEN** `TdxTradeManager.pingan.submit_ready(...)` is called without lifecycle owner-lock guard options
- **THEN** the manager MUST preserve the existing submit-ready boundary workflow
- **AND** the manager MUST NOT require lifecycle statefile ownership.

### Requirement: PingAn exception popup control SHALL remain explicit and bounded
PingAn desktop trading SHALL expose an operator-invoked exception popup control that can inspect the current result popup and close a recognized exception-like popup only when close is explicitly confirmed.

#### Scenario: Inspect reports exception popup status without side effects
- **WHEN** `TdxTradeManager.pingan.exception_popup(...)` is called with `action=inspect`
- **THEN** the manager MUST return dialog lookup, exception lookup, and result confirm lookup evidence
- **AND** the manager MUST NOT click controls, submit orders, retry, recover, resubmit, or write trade artifacts.

#### Scenario: Close requires explicit confirmation before click
- **WHEN** `TdxTradeManager.pingan.exception_popup(...)` is called with `action=close` and `confirm_close=false`
- **THEN** the manager MUST reject the request before clicking any desktop control
- **AND** the result MUST state that close was not executed and that retry, recovery, and resubmission were not executed.

#### Scenario: Close clicks only a recognized exception popup confirm control
- **WHEN** `TdxTradeManager.pingan.exception_popup(...)` is called with `action=close`, `confirm_close=true`, an exception-like result popup is detected, and its confirm control is found
- **THEN** the manager MUST click the confirm control once through the stable dialog click helper
- **AND** the result MUST record `close_executed`, `confirm_click_executed`, `retry_executed=false`, `recovery_executed=false`, `resubmission_executed=false`, and `order_submitted=false`.

#### Scenario: Close does not close non-exception result dialogs
- **WHEN** `TdxTradeManager.pingan.exception_popup(...)` is called with `action=close`, `confirm_close=true`, and no exception-like popup text is detected
- **THEN** the manager MUST NOT click the result confirm control
- **AND** the result MUST require manual review instead of treating the dialog as handled.

### Requirement: PingAn confirm-current SHALL honor broker readiness guard
PingAn confirm-current execution SHALL accept an optional broker readiness guard and MUST reject before confirm dialog lookup/click when the guard is explicitly required and broker runtime health fails.

#### Scenario: Confirm-current rejects before dialog lookup when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.confirm_current(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT perform confirm dialog lookup, confirm click, result dialog lookup, or result dialog close behavior.

#### Scenario: Confirm-current preserves default behavior when broker readiness is not required
- **WHEN** `TdxTradeManager.pingan.confirm_current(...)` is called without `require_broker_readiness`
- **THEN** the manager MUST preserve the existing confirm-current boundary workflow
- **AND** the manager MUST NOT require broker runtime health before dialog lookup.

### Requirement: PingAn buy and sell SHALL honor broker readiness guard
PingAn buy and sell desktop execution SHALL accept an optional broker readiness guard and MUST reject before buy/sell desktop automation when the guard is explicitly required and broker runtime health fails.

#### Scenario: Buy rejects before desktop automation when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.buy(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT call the buy desktop automation path.

#### Scenario: Sell rejects before desktop automation when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.sell(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT call the sell desktop automation path.

#### Scenario: Buy and sell preserve default behavior when broker readiness is not required
- **WHEN** `TdxTradeManager.pingan.buy(...)` or `TdxTradeManager.pingan.sell(...)` is called without `require_broker_readiness`
- **THEN** the manager MUST preserve the existing buy/sell risk-gate and desktop automation behavior
- **AND** the manager MUST NOT require broker runtime health before desktop dispatch.

### Requirement: PingAn submit-once SHALL honor broker readiness guard
PingAn submit-once desktop execution SHALL accept an optional broker readiness guard and MUST reject before submit-once desktop automation when the guard is explicitly required and broker runtime health fails.

#### Scenario: Buy submit-once rejects before desktop automation when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.buy_submit_once(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT call the buy submit-once desktop automation path.

#### Scenario: Sell submit-once rejects before desktop automation when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.sell_submit_once(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT call the sell submit-once desktop automation path.

#### Scenario: Submit-once preserves default behavior when broker readiness is not required
- **WHEN** `TdxTradeManager.pingan.buy_submit_once(...)` or `sell_submit_once(...)` is called without `require_broker_readiness`
- **THEN** the manager MUST preserve the existing submit-once risk-gate and desktop automation behavior
- **AND** the manager MUST NOT require broker runtime health before desktop dispatch.

### Requirement: PingAn lifecycle supervisor control SHALL remain bounded lifecycle evidence

PingAn lifecycle supervisor control SHALL remain local, operator-owned lifecycle evidence and MUST NOT imply live/manual trading acceptance or production readiness.

#### Scenario: Supervisor control evidence keeps execution boundaries explicit

- **WHEN** supervisor tick or run returns lifecycle evidence
- **THEN** the evidence MUST include `execution_mode=explicit_operator_lifecycle_supervisor_control`
- **AND** the evidence MUST include `side_effect_level=local_lifecycle_statefile` only when it writes the lifecycle statefile
- **AND** the evidence MUST include `order_submitted=false`
- **AND** the evidence MUST include `process_kill_executed=false`
- **AND** the evidence MUST include `pid_ownership_claimed=false`
- **AND** the evidence MUST include a boundary explaining that this slice records local lifecycle restart/backoff decisions and does not execute trading workflows or own the real PingAn desktop process.

### Requirement: PingAn process lifecycle control SHALL remain bounded desktop lifecycle evidence

PingAn process lifecycle control SHALL be explicit operator-owned process lifecycle evidence and MUST NOT imply broker readiness, order readiness, or live/manual trading acceptance.

#### Scenario: Process lifecycle evidence keeps boundaries explicit

- **WHEN** PingAn process lifecycle control returns status/start/stop/restart evidence
- **THEN** the evidence MUST include `execution_mode=explicit_operator_process_lifecycle_control`
- **AND** mutating actions MUST report `side_effect_level=local_lifecycle_statefile_and_process`
- **AND** the evidence MUST include `order_submitted=false`
- **AND** the evidence MUST state that only a recorded PID owned by the lifecycle statefile can be stopped or restarted
- **AND** the evidence MUST state that broker readiness, UI login readiness, workflow execution, and live/manual acceptance remain out of scope.

### Requirement: PingAn supervisor process restart SHALL remain explicit lifecycle control evidence

PingAn supervisor process restart integration SHALL remain explicit lifecycle control evidence and MUST NOT imply trading readiness or broad process ownership.

#### Scenario: Supervisor process restart boundary remains explicit

- **WHEN** supervisor process restart opt-in is enabled
- **THEN** returned evidence MUST state that process restart is delegated to the recorded-PID guarded lifecycle process controller
- **AND** returned evidence MUST include `order_submitted=false`
- **AND** returned evidence MUST not claim broker readiness, UI login readiness, retry/resubmit readiness, or live/manual acceptance.

### Requirement: PingAn post-restart readiness summary SHALL remain evidence-only

PingAn post-restart readiness summary SHALL remain lifecycle evidence and MUST NOT imply order readiness, broker production readiness, UI login readiness, or live/manual acceptance.

#### Scenario: Recheck summary preserves readiness boundaries

- **WHEN** post-restart broker health recheck evidence is returned
- **THEN** it MUST include `order_submitted=false`
- **AND** it MUST state that `lifecycle_recovery_status=recovered` only means immediate broker health recheck returned OK
- **AND** it MUST not execute task/report/catalog workflows, submit orders, retry submissions, or promote D-07/D-08 implementation status.

### Requirement: PingAn live manual acceptance evidence SHALL remain report-only

PingAn live/manual acceptance evidence SHALL be accepted only as explicit read-only report evidence and SHALL NOT execute trades, control the desktop, or promote D-07/D-08 status by itself.

#### Scenario: Manual acceptance evidence is summarized without execution

- **WHEN** a trade audit daily or period report is generated with a live/manual acceptance evidence manifest
- **THEN** the report SHALL summarize the manifest under `acceptance_outcome_coverage_status.live_manual_acceptance`
- **AND** the report SHALL keep `execution_mode=readonly_report`
- **AND** the report SHALL keep `side_effect_level=none`
- **AND** the report SHALL keep `order_submitted=false`
- **AND** the report SHALL keep `control_dispatch_executed=false`.

#### Scenario: Manual acceptance completion does not imply production readiness

- **WHEN** `live_manual_acceptance_complete=true`
- **THEN** that result SHALL mean only that the supplied manifest covers required acceptance outcomes
- **AND** it SHALL NOT prove broker production readiness, UI login readiness, order safety, or full D-07/D-08 implementation.

### Requirement: PingAn promotion readiness rollup SHALL not execute trading workflows

PingAn promotion readiness rollup SHALL aggregate existing evidence only and SHALL NOT run broker, desktop, task/report, catalog, or trade execution workflows.

#### Scenario: Rollup does not promote implemented status

- **WHEN** the rollup reports `status=complete`
- **THEN** that result SHALL remain evidence for a later status transition
- **AND** it SHALL NOT modify `FUNCTION_TREE.md`
- **AND** it SHALL NOT submit orders, control the desktop, start/stop processes, or claim production readiness.

#### Scenario: Rollup keeps source boundaries

- **WHEN** the rollup includes a complete gate
- **THEN** the rollup SHALL identify the evidence source kind
- **AND** the rollup SHALL keep boundary text stating that source files can be stale or operator-provided.

### Requirement: PingAn promotion readiness freshness gating SHALL remain read-only

The evidence freshness gate SHALL only classify evidence freshness and SHALL NOT execute any PingAn trading workflow or desktop lifecycle action.

#### Scenario: Stale evidence does not trigger workflow execution

- **WHEN** the freshness gate marks evidence stale
- **THEN** it SHALL still remain a read-only classification
- **AND** it SHALL not call broker, desktop, trade, report, or catalog execution paths.

### Requirement: PingAn promotion readiness artifact output SHALL remain evidence-only

The artifact output path SHALL persist only the already-computed promotion readiness rollup and SHALL NOT execute or refresh any PingAn trading workflow.

#### Scenario: Artifact output stays non-executing

- **WHEN** a caller writes a rollup artifact
- **THEN** the artifact SHALL record `execution_mode=readonly_evidence_rollup`
- **AND** it SHALL record no order submission or control dispatch.

### Requirement: PingAn promotion readiness manifests SHALL remain non-executing

The evidence manifest input SHALL only select existing evidence artifacts for the read-only rollup and SHALL NOT trigger broker, desktop, trade, report, catalog, or lifecycle workflow execution.

#### Scenario: Manifest input does not execute workflows

- **WHEN** a caller provides an evidence manifest
- **THEN** the task SHALL still report non-executing rollup semantics
- **AND** it SHALL not refresh source evidence or submit orders.

### Requirement: PingAn readiness manifest sample SHALL NOT satisfy live trading promotion gates

The sample manifest and its catalog/task registration SHALL be treated as discovery and wiring evidence only.

#### Scenario: Sample manifest registration remains below live readiness

- **GIVEN** a sample manifest is registered for PingAn promotion readiness rollup
- **WHEN** maintainers inspect the sample through task presets or command catalog planning
- **THEN** the sample SHALL NOT mark provider ownership as complete
- **AND** the sample SHALL NOT mark desktop lifecycle control as complete
- **AND** the sample SHALL NOT mark audit evidence as complete
- **AND** the sample SHALL NOT mark live manual acceptance as complete
- **AND** the sample SHALL NOT satisfy D-07 or D-08 implemented status by itself.

### Requirement: PingAn implemented-status promotion SHALL remain fail-closed and non-executing

The PingAn implemented-status promotion decision SHALL be a read-only gate over evidence artifacts and SHALL NOT execute trading or desktop-control workflows.

#### Scenario: Promotion decision does not execute PingAn workflows

- **GIVEN** a caller requests PingAn promotion readiness rollup
- **WHEN** the implemented-status promotion decision is built
- **THEN** broker, desktop, trade, report, task, catalog, and bundle workflows SHALL NOT be executed by the decision
- **AND** `order_submitted` SHALL remain `false`
- **AND** `control_dispatch_executed` SHALL remain `false`
- **AND** no `FUNCTION_TREE.md` status transition SHALL be executed automatically.

#### Scenario: Eligible evidence still requires explicit manual status review

- **GIVEN** all required evidence gates are complete
- **WHEN** the implemented-status promotion decision returns `eligible_for_review`
- **THEN** the decision SHALL still require manual status review
- **AND** the decision SHALL NOT claim production readiness by itself.

### Requirement: PingAn promotion evidence contract SHALL remain non-executing

The PingAn evidence provenance gate SHALL validate only source artifact schemas and SHALL NOT execute workflows.

#### Scenario: Evidence contract validation has no runtime side effects

- **GIVEN** a caller requests PingAn promotion readiness rollup
- **WHEN** the evidence contract status is built
- **THEN** broker, desktop, trade, report, task, catalog, and bundle workflows SHALL NOT be executed by the contract check
- **AND** `order_submitted` SHALL remain `false`
- **AND** `control_dispatch_executed` SHALL remain `false`
- **AND** the contract SHALL NOT prove production readiness by itself.

### Requirement: PingAn artifact provenance gate SHALL remain non-executing

The PingAn artifact provenance gate SHALL validate metadata only and SHALL NOT execute workflows.

#### Scenario: Artifact provenance validation has no runtime side effects

- **GIVEN** a caller requests PingAn promotion readiness rollup
- **WHEN** artifact provenance status is built
- **THEN** broker, desktop, trade, report, task, catalog, and bundle workflows SHALL NOT be executed by the provenance check
- **AND** `order_submitted` SHALL remain `false`
- **AND** `control_dispatch_executed` SHALL remain `false`
- **AND** artifact provenance SHALL NOT prove production readiness by itself.

### Requirement: PingAn manual acceptance recorder SHALL remain non-trading evidence capture

The PingAn live/manual acceptance recorder SHALL record operator-provided evidence only and SHALL NOT execute or infer trading workflows.

#### Scenario: Recorder boundary is explicit

- **WHEN** the recorder returns metadata
- **THEN** the metadata SHALL state that it does not execute PingAn workflows, submit orders, control the desktop, prove broker production readiness, or promote D-07/D-08 status.
