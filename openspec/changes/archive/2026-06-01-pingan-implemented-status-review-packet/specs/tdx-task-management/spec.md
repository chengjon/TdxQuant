## ADDED Requirements

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
