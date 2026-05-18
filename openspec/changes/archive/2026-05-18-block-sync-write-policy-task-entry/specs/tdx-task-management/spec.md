# tdx-task-management Delta

## ADDED Requirements

### Requirement: Task presets SHALL include a safe block sync write-policy plan

The task preset registry SHALL include a stable preset for planning a block watchlist sync with an explicit dry-run write policy.

#### Scenario: Caller runs the block sync plan preset

- **WHEN** a caller executes `task run --preset plan-zxg-block-sync-merge`
- **THEN** the task runner MUST resolve the preset to `block-sync`
- **AND** the resolved options MUST include `write_policy=merge_dry_run`
- **AND** the preset MUST not require live provider writes by default

