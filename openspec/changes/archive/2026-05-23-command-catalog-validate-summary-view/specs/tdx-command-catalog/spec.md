## ADDED Requirements

### Requirement: Command catalog validate SHALL expose opt-in summary view

The command catalog validation workflow SHALL expose an opt-in summary view that projects validation counts and non-execution status without changing the default detailed validation payload.

#### Scenario: Caller validates follow-up bundles with summary view

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the selected output payload MUST report `mode` as `validate`
- **AND** include selected kind, label, entry count, bundle count, task/report bundle count, invalid count, validation status, and non-execution status
- **AND** the workflow MUST NOT execute any task, report, trade, or bundle step

#### Scenario: Caller validates missing target with summary view

- **WHEN** a caller runs `catalog validate --bundle <missing> --view summary`
- **THEN** the command MUST still fail with invalid-request semantics
- **AND** the selected summary payload MUST include the selected missing bundle, invalid count, invalid status, and error metadata sufficient to identify the missing target

#### Scenario: Caller omits validate summary view

- **WHEN** a caller runs `catalog validate` without `--view summary`
- **THEN** the detailed validation result MUST remain the selected output payload
