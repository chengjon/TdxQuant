## MODIFIED Requirements

### Requirement: PingAn trading status promotion SHALL require explicit implementation evidence

`FUNCTION_TREE.md` SHALL keep D-07 and D-08 as `[部分实现]` until a later implementation change provides explicit evidence for provider ownership, safety gates, desktop lifecycle/result handling, audit evidence, acceptance gates, and status transition. Readonly preflight provider/safety status, readonly dialog lifecycle status, and per-result audit gate status SHALL be registered as partial promotion evidence only.

#### Scenario: D-07 and D-08 promotion plan is registered without status change

- **WHEN** the PingAn trading implemented promotion plan is registered
- **THEN** D-07 and D-08 SHALL continue to use `[部分实现]`
- **AND** their evidence SHALL cite the promotion plan
- **AND** their boundary SHALL list the remaining evidence gates before `[已实现]`.

#### Scenario: Catalog-only evidence is insufficient for implemented status

- **WHEN** D-07 or D-08 evidence only contains catalog validate, catalog plan, catalog preview, or bundle summary output
- **THEN** the FUNCTION_TREE validator and registry policy SHALL treat that evidence as read-only discovery/registration evidence
- **AND** the node boundary SHALL NOT claim broker readiness, trading safety approval, production readiness, or implemented status from that evidence alone.

#### Scenario: Preflight provider and safety gate evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites readonly PingAn `promotion_gate_status` from `trade preflight`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the gate status
- **AND** the boundary SHALL state that desktop lifecycle, audit, and acceptance gates remain before `[已实现]`.

#### Scenario: Dialog lifecycle gate evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites readonly PingAn `desktop_lifecycle_gate_status` from `trade dialog-readiness`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the gate status
- **AND** the boundary SHALL state that exception popup handling, retry policy, audit evidence, and acceptance evidence remain before `[已实现]`.

#### Scenario: Per-result audit gate evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites PingAn `trade_audit_gate_status` from finalized trade results
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the gate status
- **AND** the boundary SHALL state that complete success/failure/rejection/exception coverage and acceptance evidence remain before `[已实现]`.
