## ADDED Requirements

### Requirement: Submit-once bundle plan summary SHALL expose submit_once input-kind counts

Catalog plan/preview summary output for buy/sell submit_once bundles SHALL expose deterministic input-kind counts for selected submit_once trade plan boundaries without executing catalog dispatch or any selected step.

#### Scenario: Buy submit-once bundle plan reports submit_once_order

- **WHEN** a maintainer runs `catalog plan --bundle buy-submit-once-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_input_kind_counts.submit_once_order=1`
- **AND** the same map MUST be present in `selected_step_summary` and `plan_summary`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: Sell submit-once bundle preview reports submit_once_order

- **WHEN** a maintainer runs `catalog preview --bundle sell-submit-once-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_input_kind_counts.submit_once_order=1`
- **AND** the same map MUST be present in `selected_step_summary` and `plan_summary`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: Submit-once selected slice excluding trade boundary reports empty input-kind counts

- **WHEN** a maintainer runs `catalog plan --bundle buy-submit-once-pingan-complete-review --from-step success --view summary`
- **THEN** the summary payload MUST include an empty `trade_plan_boundary_input_kind_counts` map
- **AND** `has_trade_plan_boundary` MUST remain `false`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.
