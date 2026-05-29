## ADDED Requirements

### Requirement: Catalog bundle plan summary SHALL expose trade boundary command rollups

Catalog bundle plan and preview summary views SHALL include additive read-only `trade_plan_boundary_commands` fields derived from selected step `trade_plan_boundary.trade_command` values without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: PingAn buy bundle summary exposes trade-buy command rollup

- **WHEN** a maintainer runs `catalog plan --bundle buy-pingan-complete-review --view summary` or `catalog preview --bundle buy-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_commands` containing `trade-buy`
- **AND** the nested `selected_step_summary` and `plan_summary` MUST expose the same command list
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: PingAn sell bundle summary exposes trade-sell command rollup

- **WHEN** a maintainer runs `catalog plan --bundle sell-pingan-complete-review --view summary` or `catalog preview --bundle sell-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_commands` containing `trade-sell`
- **AND** the nested `selected_step_summary` and `plan_summary` MUST expose the same command list
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: PingAn confirm-current bundle summary exposes confirm-current command rollup

- **WHEN** a maintainer runs `catalog plan --bundle confirm-current-pingan-complete-review --view summary` or `catalog preview --bundle confirm-current-pingan-complete-review --view summary`
- **THEN** the summary payload MUST include `trade_plan_boundary_commands` containing `trade-confirm-current`
- **AND** the nested `selected_step_summary` and `plan_summary` MUST expose the same command list
- **AND** the command MUST NOT execute catalog dispatch or any selected step.
