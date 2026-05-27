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

### Requirement: FUNCTION_TREE registry SHALL validate explicit local evidence paths

The FUNCTION_TREE registry validator SHALL verify that explicit, literal repository-local paths cited as evidence in feature rows exist as checked-in files or directories, while ignoring prose, commands, symbols, glob patterns, and other non-path evidence.

#### Scenario: Feature row cites existing local evidence paths

- **WHEN** a feature row evidence cell cites literal repository-local paths such as `tests/test_function_tree_registry.py` or `scripts/validate_function_tree_registry.py`
- **AND** those paths exist under the repository root
- **THEN** the FUNCTION_TREE registry validator MUST accept those evidence references

#### Scenario: Feature row cites missing local evidence path

- **WHEN** a feature row evidence cell cites a literal repository-local path such as `tests/missing_registry_test.py`
- **AND** that path does not exist under the repository root
- **THEN** the FUNCTION_TREE registry validator MUST fail with the row id and missing path

#### Scenario: Feature row cites non-literal evidence

- **WHEN** a feature row evidence cell cites non-path evidence such as function names, command examples, OpenSpec ids, or globbed paths such as `runtime/trade-audits/*`
- **THEN** the FUNCTION_TREE registry validator MUST NOT require those values to exist as literal repository paths

### Requirement: FUNCTION_TREE registry validator SHALL expose JSON report output

The FUNCTION_TREE registry validator SHALL expose an opt-in JSON report for machine consumers while preserving the default text output and exit-code semantics.

#### Scenario: Maintainer requests successful JSON report

- **WHEN** a maintainer runs the FUNCTION_TREE registry validator with `--json` against a valid repository root
- **THEN** the validator MUST print a JSON object to stdout
- **AND** the JSON object MUST include `valid`, `row_count`, `status_counts`, `problem_count`, and `errors`
- **AND** `valid` MUST be true, `problem_count` MUST be `0`, and `errors` MUST be empty

#### Scenario: Maintainer requests failing JSON report

- **WHEN** a maintainer runs the FUNCTION_TREE registry validator with `--json` against an invalid registry
- **THEN** the validator MUST return the same non-zero exit code it would return in text mode
- **AND** the JSON object MUST include the validation errors in `errors`
- **AND** stderr MUST remain empty so machine consumers can read the report from a single stream

#### Scenario: Maintainer omits JSON flag

- **WHEN** a maintainer runs the FUNCTION_TREE registry validator without `--json`
- **THEN** the existing compact text summary and stderr error output MUST remain unchanged

### Requirement: FUNCTION_TREE lifecycle material status SHALL be explicitly bounded

The FUNCTION_TREE registry SHALL allow the OpenSpec lifecycle material node to be marked implemented when the registry validator, evidence checks, tests, and machine-readable report are present, provided the node boundary clearly states that the validator does not prove downstream feature runtime availability.

#### Scenario: Lifecycle material node is implemented with validation evidence

- **WHEN** the lifecycle material node cites the validator script, validator tests, OpenSpec evidence checks, local evidence path checks, ROADMAP rejection, and JSON report output
- **THEN** the node MAY be registered as `[已实现]`
- **AND** the boundary MUST state that the validator does not execute evidence paths or prove cited feature availability

#### Scenario: Lifecycle status does not affect downstream feature status

- **WHEN** the lifecycle material node is registered as `[已实现]`
- **THEN** other feature nodes MUST retain their own explicit status, evidence, and boundary

### Requirement: FUNCTION_TREE registry SHALL record external tdx merge decisions

The FUNCTION_TREE registry SHALL record merged external `tdx` evidence and capability decisions without allowing external documentation to become a competing source of feature truth.

#### Scenario: External tdx evidence is accepted
- **WHEN** implementation accepts a feature or validation conclusion from `D:\MyCode3\tdx`
- **THEN** the affected FUNCTION_TREE row MUST cite current checked-in evidence, an active OpenSpec change, an archived OpenSpec change, or an explicit external evidence reference
- **AND** the row boundary MUST state the usable scope of the accepted evidence

#### Scenario: External tdx evidence is rejected or deferred
- **WHEN** implementation rejects or defers an external `tdx` feature claim
- **THEN** the affected FUNCTION_TREE row MUST keep or adopt a boundary that prevents the feature from reading as currently available
- **AND** the rejection or deferral rationale MUST be traceable from the merge change tasks or docs

### Requirement: FUNCTION_TREE registry SHALL keep PingAn and TongDaXin trading status separate

The FUNCTION_TREE registry SHALL avoid collapsing PingAn desktop trading evidence and TongDaXin trading bridge evidence into one generic desktop-trading status.

#### Scenario: PingAn mixed-chain execution is registered
- **WHEN** PingAn real-machine validation is adopted
- **THEN** the registry MUST identify PingAn execution as a mixed UIA/HID/Win32 desktop chain
- **AND** it MUST NOT describe the capability as pure background Win32 automation

#### Scenario: TongDaXin trading probe boundary is registered
- **WHEN** TongDaXin trading bridge evidence is registered
- **THEN** the registry MUST distinguish probe or diagnostic capability from full live order submission
- **AND** it MUST mark full TongDaXin order submission as unavailable unless business-layer security-code acceptance is evidenced
