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

D-07 and D-08 SHALL remain `[部分实现]` until implementation evidence covers all ordered promotion gates. Readonly provider/broker ownership plus safety preflight status SHALL count only as the first partial promotion gate and SHALL NOT by itself satisfy live trading implementation.

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
