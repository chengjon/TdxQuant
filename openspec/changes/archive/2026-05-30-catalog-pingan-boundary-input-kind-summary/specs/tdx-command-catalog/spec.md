## ADDED Requirements

### Requirement: PingAn bundle plan summary SHALL expose trade boundary input-kind counts

Catalog plan/preview summary output for PingAn buy/sell/confirm_current bundles SHALL expose deterministic input-kind counts for selected trade plan boundaries without executing catalog dispatch or any selected step.

#### Scenario: Buy bundle plan reports order input kind

- **WHEN** a maintainer runs `catalog plan --bundle buy-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_input_kind_counts.order=1`
- **AND** the same map MUST be present in `selected_step_summary` and `plan_summary`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: Confirm-current bundle preview reports confirmation input kind

- **WHEN** a maintainer runs `catalog preview --bundle confirm-current-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_input_kind_counts.confirmation=1`
- **AND** the same map MUST be present in `selected_step_summary` and `plan_summary`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: Selected slice excluding trade boundary reports empty input-kind counts

- **WHEN** a maintainer runs `catalog plan --bundle buy-pingan-complete-review --from-step success --view summary`
- **THEN** the summary payload MUST include an empty `trade_plan_boundary_input_kind_counts` map
- **AND** `has_trade_plan_boundary` MUST remain `false`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.
