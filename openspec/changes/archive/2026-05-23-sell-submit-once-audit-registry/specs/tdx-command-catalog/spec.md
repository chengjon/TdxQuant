## ADDED Requirements

### Requirement: Command catalog SHALL expose Ping An sell submit-once audit diagnostics

The command catalog SHALL expose Ping An `sell_submit_once` report entries and bundles without requiring a separate roadmap document.

#### Scenario: Caller lists Ping An sell submit-once audit catalog entries

- **WHEN** a caller filters command catalog entries by `sell-submit-once`
- **THEN** the catalog MUST include daily and period Ping An `sell_submit_once` exception, rejected, and failed report entries

#### Scenario: Caller plans Ping An sell submit-once follow-up bundle

- **WHEN** a caller plans a Ping An sell submit-once follow-up bundle
- **THEN** the plan MUST include a `task-submit-once` step with `side=sell`
- **AND** the plan MUST include the matching Ping An `sell_submit_once` audit report entry
