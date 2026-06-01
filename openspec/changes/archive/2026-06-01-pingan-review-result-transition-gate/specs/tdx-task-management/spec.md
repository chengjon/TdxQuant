## ADDED Requirements

### Requirement: PingAn implemented-status transition gate SHALL validate review results without transitioning status

`TdxTaskManager.pingan_implemented_status_transition_gate(...)` SHALL validate a PingAn implemented-status review result artifact and return a read-only transition gate without editing FUNCTION_TREE status or executing PingAn workflows.

#### Scenario: Approved review result passes transition gate

- **GIVEN** a review result artifact uses schema `tdx.desktop_trade.pingan_implemented_status_review_result.v1`
- **AND** artifact provenance identifies `source_kind=implemented_status_review_result`, `producer=task pingan-implemented-status-review-result`, and the expected evidence schema
- **AND** the artifact has `outcome=approve`
- **AND** it targets `D-07` and `D-08`
- **AND** packet fields show `packet_review_status=ready_for_manual_review`, `packet_decision=eligible_for_review`, and `implemented_status_eligible=true`
- **WHEN** the task validates the transition gate
- **THEN** it SHALL return `implemented_status_transition_gate`
- **AND** the gate SHALL use schema `tdx.desktop_trade.pingan_implemented_status_transition_gate.v1`
- **AND** `gate_status` SHALL be `eligible_for_status_transition_review`
- **AND** `eligible_for_status_transition_review` SHALL be true
- **AND** `function_tree_status_transition_executed` SHALL be false
- **AND** `manual_status_transition_required` SHALL be true.

#### Scenario: Non-approved review result is blocked

- **GIVEN** a review result artifact has `outcome=reject` or `outcome=defer`
- **WHEN** the task validates the transition gate
- **THEN** the gate SHALL use `gate_status=blocked`
- **AND** `eligible_for_status_transition_review` SHALL be false
- **AND** `blocked_reasons` SHALL include `review_result_not_approved`
- **AND** no FUNCTION_TREE status transition SHALL be executed.

#### Scenario: Invalid review result provenance is blocked

- **GIVEN** a review result artifact has missing or mismatched artifact provenance
- **WHEN** the task validates the transition gate
- **THEN** the gate SHALL use `gate_status=blocked`
- **AND** `blocked_reasons` SHALL include `unverified_review_result_artifact_provenance`
- **AND** no FUNCTION_TREE status transition SHALL be executed.

#### Scenario: Transition gate remains read-only

- **WHEN** the task returns transition gate metadata
- **THEN** `execution_mode` SHALL be `readonly_status_transition_gate`
- **AND** `side_effect_level` SHALL be `none`
- **AND** `order_submitted` SHALL be false
- **AND** `control_dispatch_executed` SHALL be false
- **AND** `function_tree_status_transition_executed` SHALL be false.
