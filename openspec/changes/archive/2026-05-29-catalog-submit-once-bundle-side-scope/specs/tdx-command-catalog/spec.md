## ADDED Requirements

### Requirement: Command catalog bundle plan SHALL preserve side-specific bundle step side
Command catalog bundle plan and preview summaries SHALL prevent top-level submit-once side overrides from changing side-specific bundle step metadata.

#### Scenario: Sell submit-once bundle ignores top-level buy side override
- **WHEN** a caller runs `catalog plan --bundle sell-submit-once-pingan-complete-review --side buy --view summary`
- **THEN** the first step `trade_plan_boundary.side` MUST remain `sell`
- **AND** planning MUST NOT execute the submit-once workflow

#### Scenario: Entry side override remains available
- **WHEN** a caller runs `catalog plan --entry submit-once --side sell --view summary`
- **THEN** the entry `trade_plan_boundary.side` MUST be `sell`
- **AND** planning MUST NOT execute the submit-once workflow

