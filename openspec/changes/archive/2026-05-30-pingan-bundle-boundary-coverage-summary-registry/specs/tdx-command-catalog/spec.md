## ADDED Requirements

### Requirement: Catalog bundle plan summary SHALL expose trade boundary input coverage status counts

Catalog bundle plan and preview summary views SHALL include additive read-only `trade_plan_boundary_input_coverage_status_counts` fields derived from selected step `trade_plan_boundary.input_coverage_status` values without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: PingAn buy bundle reports missing required input coverage status

- **WHEN** a maintainer runs `catalog plan --bundle buy-pingan-complete-review --view summary` or `catalog preview --bundle buy-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_input_coverage_status_counts.missing_required_inputs=1`
- **AND** the nested `selected_step_summary` and `plan_summary` MUST expose the same counts
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: PingAn confirm-current bundle reports no-required-input coverage status

- **WHEN** a maintainer runs `catalog plan --bundle confirm-current-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_input_coverage_status_counts.no_required_inputs=1`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: PingAn bundle slice excluding trade boundaries reports empty coverage counts

- **WHEN** a maintainer runs `catalog plan --bundle buy-pingan-complete-review --from-step success --view summary`
- **THEN** the summary payload MUST include an empty `trade_plan_boundary_input_coverage_status_counts` map
- **AND** `has_trade_plan_boundary` MUST remain `false`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.
