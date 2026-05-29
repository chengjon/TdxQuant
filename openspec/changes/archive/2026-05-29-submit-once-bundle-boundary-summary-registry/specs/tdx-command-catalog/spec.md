## MODIFIED Requirements

### Requirement: Command catalog plan summary SHALL expose selected step source counts

The command catalog SHALL include a compact `step_source_counts` object in bundle `plan` and `preview` summary views, derived from the selected resolved steps without executing catalog dispatch.

#### Scenario: Submit-once buy bundle summary exposes trade boundary rollup

- **WHEN** a maintainer runs `catalog plan --bundle buy-submit-once-pingan-complete-review --view summary` or `catalog preview --bundle buy-submit-once-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_step_count` equal to the number of selected steps with `trade_plan_boundary`
- **AND** the summary payload MUST include `trade_plan_boundary_sides` containing `buy`
- **AND** the nested `plan_summary` MUST expose the same count and side list
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: Submit-once sell bundle summary exposes trade boundary rollup

- **WHEN** a maintainer runs `catalog plan --bundle sell-submit-once-pingan-complete-review --view summary` or `catalog preview --bundle sell-submit-once-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_step_count` equal to the number of selected steps with `trade_plan_boundary`
- **AND** the summary payload MUST include `trade_plan_boundary_sides` containing `sell`
- **AND** the nested `plan_summary` MUST expose the same count and side list
- **AND** the command MUST NOT execute catalog dispatch or any selected step.
