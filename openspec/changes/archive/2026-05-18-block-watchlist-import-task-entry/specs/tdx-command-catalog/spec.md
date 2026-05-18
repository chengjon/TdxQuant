# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog SHALL expose a plan-able block watchlist import entry

The command catalog SHALL expose a task-source entry for the JSON watchlist import wrapper so callers can discover and plan the import path without executing provider mutations.

#### Scenario: Caller lists block import catalog entries

- **WHEN** a caller lists catalog entries with the `block` or `import` label
- **THEN** the catalog MUST include a task-source entry for block watchlist import

#### Scenario: Caller plans a block import catalog entry

- **WHEN** a caller executes `catalog plan --entry <block-import-entry>`
- **THEN** the plan MUST resolve to the task command and include the preset-owned import path without dispatching execution
