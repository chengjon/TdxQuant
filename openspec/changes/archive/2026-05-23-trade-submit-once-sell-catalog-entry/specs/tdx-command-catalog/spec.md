## ADDED Requirements

### Requirement: Command catalog SHALL expose a side-explicit sell submit-once task entry

The command catalog SHALL expose a side-explicit sell submit-once task entry and use it for Ping An sell submit-once follow-up bundles.

#### Scenario: Caller lists the sell submit-once task catalog entry

- **WHEN** a caller filters command catalog entries by `sell-submit-once`
- **THEN** the catalog MUST include `task-sell-submit-once`
- **AND** the entry MUST resolve to the `sell-submit-once-default` task preset

#### Scenario: Caller plans a Ping An sell submit-once follow-up bundle

- **WHEN** a caller plans a Ping An sell submit-once follow-up bundle with explicit `code`, `price`, and `quantity`
- **THEN** the plan MUST include a task step whose entry is `task-sell-submit-once`
- **AND** the task step MUST resolve to `trade-submit-once` with `side=sell`
- **AND** the plan MUST include the matching existing Ping An sell submit-once audit report preset
- **AND** planning MUST remain non-executing
