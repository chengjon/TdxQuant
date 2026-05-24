# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog trade plan summary SHALL expose non-execution trade input boundaries

The command catalog SHALL include a `trade_plan_boundary` in plan/preview summary views for trade-related catalog entries and selected bundle steps, derived from resolved dispatch metadata and arguments without executing catalog dispatch.

#### Scenario: Caller plans a trade entry with summary view

- **WHEN** a caller executes `catalog plan --entry <trade-entry> --view summary`
- **THEN** the summary view MUST include `trade_plan_boundary`
- **AND** the boundary MUST include the resolved trade command, non-executing execution mode, dispatch-executed flag, required input fields, provided input fields, and missing input fields
- **AND** the plan MUST retain non-execution provenance and constraints
- **AND** the underlying trade/task dispatch workflow MUST NOT be invoked

#### Scenario: Caller plans a submit-once entry with summary view

- **WHEN** a caller executes `catalog plan --entry <submit-once-entry> --view summary`
- **THEN** `trade_plan_boundary` MUST include the resolved submit-once side when present
- **AND** it MUST report the submit-once input fields without executing trade dispatch

#### Scenario: Caller plans a trade follow-up bundle with summary view

- **WHEN** a caller executes `catalog plan --bundle <trade-follow-up-bundle> --view summary`
- **THEN** each selected trade-related step MUST include a `trade_plan_boundary`
- **AND** selected report-only steps MUST NOT be marked as trade plan boundaries
- **AND** the bundle plan MUST remain non-executing

