## ADDED Requirements

### Requirement: PingAn trading status promotion SHALL require explicit implementation evidence

`FUNCTION_TREE.md` SHALL keep D-07 and D-08 as `[部分实现]` until a later implementation change provides explicit evidence for provider ownership, safety gates, desktop lifecycle/result handling, audit evidence, acceptance gates, and status transition.

#### Scenario: D-07 and D-08 promotion plan is registered without status change

- **WHEN** the PingAn trading implemented promotion plan is registered
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** D-08 MUST remain `[部分实现]`
- **AND** both rows MUST cite the promotion plan as a future implementation gate
- **AND** both rows MUST NOT imply broker readiness, trading safety approval, production readiness, or complete desktop exception coverage.

#### Scenario: Catalog-only evidence is insufficient for implemented status

- **WHEN** D-07 or D-08 cites catalog validate/plan/preview evidence
- **THEN** that evidence MUST be treated as read-only discovery or summary evidence
- **AND** it MUST NOT be sufficient by itself to move the row to `[已实现]`.
