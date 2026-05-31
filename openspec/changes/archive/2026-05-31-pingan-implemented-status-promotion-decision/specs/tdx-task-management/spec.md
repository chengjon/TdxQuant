## ADDED Requirements

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
