## ADDED Requirements

### Requirement: Command catalog SHALL expose direct submit-once plan boundary
The command catalog SHALL expose direct trade-source submit-once input coverage metadata in non-executing plan and preview summaries while reusing the existing submit-once preset behavior.

#### Scenario: Caller lists the direct submit-once trade entry
- **WHEN** a caller lists catalog entries with a `submit-once` label
- **THEN** the catalog MUST include the direct `submit-once` trade entry
- **AND** the entry MUST resolve to a trade preset whose command is `submit-once`

#### Scenario: Caller plans the direct submit-once trade entry
- **WHEN** a caller plans the direct `submit-once` trade entry with order inputs
- **THEN** the plan summary MUST include trade input boundary metadata for command `submit-once`
- **AND** the boundary MUST include the resolved default side
- **AND** planning MUST NOT execute the submit-once workflow

#### Scenario: Missing direct submit-once inputs remain explicit
- **WHEN** a caller plans the direct `submit-once` trade entry without order inputs
- **THEN** the plan summary MUST report missing `code`, `price`, and `quantity`
- **AND** the plan summary MUST keep the non-execution constraints intact

