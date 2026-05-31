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
