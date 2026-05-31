## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL cite PingAn promotion decision as partial mainline evidence

`FUNCTION_TREE.md` SHALL register the implemented-status promotion decision as mainline evidence for D-07/D-08 while keeping both nodes partial until a later explicit status-transition change is completed.

#### Scenario: D-07 and D-08 remain partial after promotion-decision implementation

- **GIVEN** the PingAn implemented-status promotion decision exists
- **WHEN** D-07 and D-08 cite it as evidence
- **THEN** both nodes SHALL remain `[部分实现]`
- **AND** both nodes SHALL cite `implemented_status_promotion_decision`
- **AND** both nodes SHALL cite `eligible_for_review`
- **AND** both nodes SHALL cite `blocked_reasons`
- **AND** both nodes SHALL cite the OpenSpec change `pingan-implemented-status-promotion-decision`
- **AND** both node boundaries SHALL say the decision is read-only and fail-closed
- **AND** both node boundaries SHALL say it does not execute PingAn workflows
- **AND** both node boundaries SHALL say it does not automatically edit FUNCTION_TREE status.
