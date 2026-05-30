## ADDED Requirements

### Requirement: Submit-once bundle plan summary SHALL expose input coverage status counts

Submit-once bundle plan and preview summary views SHALL expose additive read-only `trade_plan_boundary_input_coverage_status_counts` fields derived from selected step `trade_plan_boundary.input_coverage_status` values without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Buy submit-once bundle reports missing required input coverage

- **WHEN** a maintainer runs `catalog plan --bundle buy-submit-once-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_input_coverage_status_counts.missing_required_inputs=1`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: Sell submit-once bundle preview reports missing required input coverage

- **WHEN** a maintainer runs `catalog preview --bundle sell-submit-once-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_input_coverage_status_counts.missing_required_inputs=1`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: Submit-once bundle slice excluding the trade step reports empty coverage counts

- **WHEN** a maintainer runs `catalog plan --bundle buy-submit-once-pingan-complete-review --from-step success --view summary`
- **THEN** the summary payload MUST include an empty `trade_plan_boundary_input_coverage_status_counts` map
- **AND** `has_trade_plan_boundary` MUST remain `false`
- **AND** the command MUST NOT execute catalog dispatch or any selected step.
