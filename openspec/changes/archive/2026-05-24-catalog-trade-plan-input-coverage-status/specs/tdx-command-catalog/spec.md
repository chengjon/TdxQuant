# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog trade plan boundary SHALL expose input coverage status

Catalog plan and preview summary views SHALL include an additive `trade_plan_boundary.input_coverage_status` field for trade-related catalog entries and selected bundle steps, derived only from existing required/provided/missing input fields and without executing catalog dispatch.

#### Scenario: Missing order inputs are explicit

- **WHEN** a caller executes `catalog plan --entry <trade-entry> --view summary` without all required order inputs
- **THEN** `trade_plan_boundary.input_coverage_status` MUST be `missing_required_inputs`
- **AND** `trade_plan_boundary.missing_input_count` MUST be greater than zero
- **AND** `trade_plan_boundary.dispatch_executed` MUST remain `false`

#### Scenario: Complete order inputs are explicit

- **WHEN** a caller executes `catalog plan --entry <trade-entry> --view summary` with all required order inputs resolved
- **THEN** `trade_plan_boundary.input_coverage_status` MUST be `complete`
- **AND** `trade_plan_boundary.missing_input_count` MUST be zero
- **AND** the summary MUST remain non-executing

#### Scenario: No-input confirmation commands are explicit

- **WHEN** a caller executes `catalog plan --entry <confirm-current-entry> --view summary`
- **THEN** `trade_plan_boundary.input_coverage_status` MUST be `no_required_inputs`
- **AND** required, provided, and missing input counts MUST all be zero
- **AND** the summary MUST remain non-executing
