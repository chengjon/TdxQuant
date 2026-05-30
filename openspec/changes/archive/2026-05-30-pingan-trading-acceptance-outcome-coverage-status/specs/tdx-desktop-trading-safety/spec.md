## MODIFIED Requirements

### Requirement: PingAn live trading implementation SHALL be gated by safety and acceptance evidence

D-07 and D-08 SHALL remain `[部分实现]` until implementation evidence covers all ordered promotion gates. Readonly provider/broker ownership plus safety preflight status, readonly desktop dialog lifecycle status, per-result audit gate status, and read-only acceptance outcome coverage status SHALL count only as partial promotion evidence and SHALL NOT by themselves satisfy live trading implementation.

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

#### Scenario: Read-only acceptance outcome coverage evidence remains partial

- **WHEN** D-07 or D-08 evidence includes PingAn `acceptance_outcome_coverage_status` from trade audit reports
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the payload is read-only report evidence
- **AND** the boundary MUST separately list missing automated outcome statuses and missing live/manual acceptance evidence before `[已实现]`.

