## ADDED Requirements

### Requirement: Catalog validate summary SHALL expose validation outcome

`catalog validate --view summary` SHALL include additive read-only `validation_outcome` metadata derived from existing validation summary fields without executing catalog entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.

#### Scenario: Bundle validation summary includes outcome

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `validation_outcome`
- **AND** the object MUST derive kind, selected label, entry count, bundle count, invalid count, validity, non-execution flag, result code, and result message from existing summary siblings
- **AND** `has_invalid_entries` MUST be false when the existing invalid count is zero
- **AND** the summary MUST NOT include raw `entries` or raw `bundles`

#### Scenario: Outcome remains non-executing

- **WHEN** catalog validation reports `validation_outcome`
- **THEN** the object MUST NOT indicate that any entry, bundle, task/report step, trade command, provider call, or workflow action was executed
- **AND** existing count maps and family summary objects MUST remain available
