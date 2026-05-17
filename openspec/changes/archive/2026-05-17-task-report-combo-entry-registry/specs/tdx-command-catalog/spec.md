# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog SHALL expose tested task/report combo bundles for daily follow-up workflows

The system SHALL expose stable named catalog bundles that compose at least one task-source entry with one or more report-source entries for daily follow-up workflows, while preserving the existing bundle planning and dispatch model.

#### Scenario: Caller discovers task/report combo bundles by label

- **WHEN** a caller lists catalog bundles with a follow-up label filter
- **THEN** the catalog MUST include at least one bundle composed from both task-source and report-source entries

#### Scenario: Caller plans a task/report combo bundle without execution

- **WHEN** a caller plans a task/report combo bundle such as `confirm-complete-review`
- **THEN** the plan MUST include the resolved task step and report steps without dispatching execution
- **AND** the selected-step metadata MUST identify the full bundle step count

#### Scenario: Task/report combo bundles preserve existing execution boundaries

- **WHEN** a task/report combo bundle is listed or planned
- **THEN** the system MUST treat it as a composition of existing catalog entries rather than a new task, report, or trading capability contract
