## ADDED Requirements

### Requirement: Command catalog SHALL expose ordinary Ping An sell task follow-up bundles

The command catalog SHALL expose the existing ordinary sell task workflow and fixed Ping An sell audit follow-up bundles without adding new sell execution semantics.

#### Scenario: Caller lists the task sell catalog entry

- **WHEN** a caller filters command catalog entries by `sell`
- **THEN** the catalog MUST include `task-sell`
- **AND** the entry MUST resolve to the `task-sell-default` task preset

#### Scenario: Caller plans an ordinary Ping An sell follow-up bundle with explicit order inputs

- **WHEN** a caller plans an ordinary Ping An sell follow-up bundle with explicit `code`, `price`, and `quantity`
- **THEN** the plan MUST include a task step resolving to `trade-sell`
- **AND** the plan MUST include the matching existing Ping An sell audit report preset
- **AND** planning MUST remain non-executing
