## ADDED Requirements

### Requirement: Catalog bundle plan summary SHALL expose selected-step trade boundary presence

Catalog bundle plan and preview summary views SHALL include additive read-only `has_trade_plan_boundary` fields derived from selected step `trade_plan_boundary` presence without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: PingAn bundle slice excluding trade steps reports no trade boundary

- **WHEN** a maintainer runs `catalog plan --bundle buy-pingan-complete-review --from-step success --view summary` or `catalog preview --bundle buy-pingan-complete-review --from-step success --view summary`
- **THEN** the summary payload MUST include `has_trade_plan_boundary=false`
- **AND** `trade_plan_boundary_step_count` MUST be `0`
- **AND** the nested `selected_step_summary` and `plan_summary` MUST expose the same boolean
- **AND** the command MUST NOT execute catalog dispatch or any selected step.

#### Scenario: PingAn bundle slice including only the trade step reports a trade boundary

- **WHEN** a maintainer runs `catalog plan --bundle buy-pingan-complete-review --to-step trade --view summary`
- **THEN** the summary payload MUST include `has_trade_plan_boundary=true`
- **AND** `trade_plan_boundary_step_count` MUST be `1`
- **AND** `trade_plan_boundary_commands` MUST contain `trade-buy`
- **AND** the nested `selected_step_summary` and `plan_summary` MUST expose the same boolean
- **AND** the command MUST NOT execute catalog dispatch or any selected step.
