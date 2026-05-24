# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog trade plan boundary SHALL expose input coverage counts

Catalog plan and preview summary views SHALL include additive input coverage counts in `trade_plan_boundary` for trade-related catalog entries and selected bundle steps, derived from existing field lists without executing catalog dispatch.

#### Scenario: Trade entry summary includes input counts

- **WHEN** a caller executes `catalog plan --entry <trade-entry> --view summary`
- **THEN** `trade_plan_boundary.required_input_count` MUST equal the number of required input fields
- **AND** `trade_plan_boundary.provided_input_count` MUST equal the number of provided input fields
- **AND** `trade_plan_boundary.missing_input_count` MUST equal the number of missing input fields
- **AND** `trade_plan_boundary.dispatch_executed` MUST remain `false`

#### Scenario: Submit-once summary includes side and input counts

- **WHEN** a caller executes `catalog plan --entry <submit-once-entry> --view summary`
- **THEN** `trade_plan_boundary.side` MUST remain present when resolved
- **AND** input coverage counts MUST be derived from the submit-once boundary field lists
- **AND** the summary MUST remain non-executing

#### Scenario: Trade bundle step summary includes input counts

- **WHEN** a caller executes `catalog plan --bundle <trade-follow-up-bundle> --view summary`
- **THEN** each selected trade-related step with `trade_plan_boundary` MUST include input coverage counts
- **AND** non-trade steps MUST continue to omit `trade_plan_boundary`
- **AND** the bundle plan MUST remain non-executing
