# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog SHALL expose a plan-able block sync write-policy entry

The command catalog SHALL expose a task-source entry for the safe block sync write-policy preset so callers can discover and plan the workflow without implying that provider mutation is automatic.

#### Scenario: Caller lists block sync catalog entries

- **WHEN** a caller lists catalog entries with the `block`, `sync`, or `dry-run` label
- **THEN** the catalog MUST include a task-source entry for the block sync write-policy plan

#### Scenario: Caller plans a block sync catalog entry

- **WHEN** a caller executes `catalog plan --entry plan-zxg-block-sync-merge`
- **THEN** the plan MUST resolve to the task command and include the explicit dry-run write policy without dispatching execution

