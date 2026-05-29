## ADDED Requirements

### Requirement: Command catalog plan and preview SHALL support submit-once side override
The command catalog SHALL allow non-executing plan and preview summaries to override submit-once side metadata without widening catalog run execution.

#### Scenario: Caller plans direct submit-once with sell side
- **WHEN** a caller runs `catalog plan --entry submit-once --side sell --view summary`
- **THEN** the plan summary MUST include `trade_plan_boundary.side=sell`
- **AND** planning MUST NOT execute the submit-once workflow

#### Scenario: Caller previews task submit-once with sell side
- **WHEN** a caller runs `catalog preview --entry task-submit-once --side sell --view summary`
- **THEN** the preview summary MUST include `trade_plan_boundary.side=sell`
- **AND** preview MUST NOT execute the task workflow

#### Scenario: Catalog run execution surface remains unchanged
- **WHEN** a caller tries to pass `--side` to `catalog run`
- **THEN** the parser MUST reject the argument
- **AND** no catalog entry or workflow MUST be dispatched

