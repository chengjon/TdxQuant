## ADDED Requirements

### Requirement: Catalog plan summary SHALL expose plan outcome

`catalog plan --view summary` and `catalog preview --view summary` SHALL include additive read-only `plan_outcome` metadata derived from existing plan summary fields and non-execution constraints without executing catalog entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.

#### Scenario: Bundle plan summary includes outcome

- **WHEN** a caller runs `catalog plan --bundle confirm-complete-review --view summary`
- **THEN** the summary payload MUST include `plan_outcome`
- **AND** the object MUST derive mode, target type/name, selected step count, step-source key count, result code, and result message from existing summary siblings
- **AND** `non_execution` MUST be true only when existing constraints indicate non-executing mode and no dispatch execution
- **AND** existing `constraints`, `steps`, step count maps, and summary fields MUST remain available

#### Scenario: Plan outcome remains non-executing

- **WHEN** catalog plan or preview reports `plan_outcome`
- **THEN** the object MUST NOT indicate that any entry, bundle, task/report step, trade command, provider call, or workflow action was executed
- **AND** the summary MUST NOT claim workflow-builder support, broker readiness, trade safety approval, or execution coverage
