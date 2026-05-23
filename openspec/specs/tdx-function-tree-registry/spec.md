# tdx-function-tree-registry Specification

## Purpose
TBD - created by archiving change function-tree-registry-validator. Update Purpose after archive.
## Requirements
### Requirement: FUNCTION_TREE registry SHALL be mechanically validatable

The project SHALL provide a repeatable validation script for `FUNCTION_TREE.md`
so the feature registry can remain the single source of feature truth without a
competing roadmap document.

#### Scenario: Current registry passes validation

- **WHEN** a maintainer runs the FUNCTION_TREE registry validator against the repository root
- **THEN** the validator MUST accept the current `FUNCTION_TREE.md`
- **AND** it MUST print a compact count of validated rows by status

#### Scenario: Feature rows require explicit state, evidence, and boundary

- **WHEN** a feature row has an unsupported status, duplicate id, empty evidence, or empty boundary
- **THEN** the validator MUST fail with an actionable error

#### Scenario: Designed or pending rows cannot read as available

- **WHEN** a feature row is marked `[已设计/待实现]`
- **THEN** the validator MUST require boundary language that explicitly signals pending, unavailable, or not-implemented status

#### Scenario: Competing roadmap document is rejected

- **WHEN** a repository root contains `ROADMAP.md`
- **THEN** the validator MUST fail so `FUNCTION_TREE.md` remains the single feature registry

### Requirement: FUNCTION_TREE registry SHALL validate cited OpenSpec evidence

The FUNCTION_TREE registry validator SHALL verify that OpenSpec change ids cited
as evidence in feature rows resolve to checked-in active or archived OpenSpec
change material.

#### Scenario: Feature row cites archived OpenSpec evidence

- **WHEN** a feature row evidence cell cites `OpenSpec `some-change``
- **AND** `openspec/changes/archive/<date>-some-change/` exists
- **THEN** the FUNCTION_TREE registry validator MUST accept that evidence reference

#### Scenario: Feature row cites active OpenSpec evidence

- **WHEN** a feature row evidence cell cites `OpenSpec `some-change``
- **AND** `openspec/changes/some-change/.openspec.yaml` exists
- **THEN** the FUNCTION_TREE registry validator MUST accept that evidence reference

#### Scenario: Feature row cites missing OpenSpec evidence

- **WHEN** a feature row evidence cell cites an OpenSpec change id that does not exist as an active or archived change
- **THEN** the FUNCTION_TREE registry validator MUST fail with the row id and missing change id
