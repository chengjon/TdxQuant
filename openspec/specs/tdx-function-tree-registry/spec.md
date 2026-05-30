# tdx-function-tree-registry Specification

## Purpose
TBD - created by archiving change function-tree-registry-validator. Update Purpose after archive.
## Requirements
### Requirement: FUNCTION_TREE registry SHALL be mechanically validatable

`FUNCTION_TREE.md` SHALL remain a single feature registry where each feature row carries explicit status, evidence, and boundary text that can be mechanically validated.

#### Scenario: D-08 submit_once input-kind rollup evidence stays bounded

- **WHEN** D-08 cites submit_once bundle input-kind count evidence
- **THEN** D-08 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade_plan_boundary_input_kind_counts` and `submit_once_order`
- **AND** the boundary MUST state that the field is read-only catalog plan/preview summary evidence
- **AND** the row MUST NOT imply catalog run execution, broker readiness, trading safety approval, production readiness, or independent desktop submit_once primitives.

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

The FUNCTION_TREE registry SHALL allow lifecycle-related feature nodes to be marked implemented when their evidence, tests, and boundaries describe the implemented lifecycle surface without implying downstream runtime availability.

#### Scenario: Subscription long-run control nodes are implemented with bounded evidence

- **WHEN** B-16 and E-09 cite persisted start requests, explicit restart, restart preflight, restart observation, bounded restart backoff, supervisor tick/run, supervisor daemon controls, statefile ownership diagnostics, lifecycle readiness, diagnostics/runbook projections, tests, and OpenSpec evidence
- **THEN** B-16 and E-09 MAY be registered as `[已实现]`
- **AND** their boundaries MUST state that the implemented surface is explicit operator-managed subscription watch lifecycle control and diagnostics
- **AND** their boundaries MUST NOT imply automatic production recovery, live TongDaXin provider availability, broker readiness, trading readiness, workflow execution, or a complete provider lifecycle guarantee.

#### Scenario: Subscription long-run implemented status remains isolated

- **WHEN** B-16 and E-09 are registered as `[已实现]`
- **THEN** D-07, D-08, E-11, and other feature nodes MUST retain their own explicit statuses, evidence, and boundaries.

### Requirement: PingAn trading status promotion SHALL require explicit implementation evidence

`FUNCTION_TREE.md` SHALL keep D-07 and D-08 as `[部分实现]` until a later implementation change provides explicit evidence for provider ownership, safety gates, desktop lifecycle/result handling, audit evidence, acceptance gates, and status transition. Readonly preflight provider/safety status, readonly dialog lifecycle status, per-result audit gate status, read-only acceptance outcome coverage status, explicit exception audit outcome status, and failed audit classification status SHALL be registered as partial promotion evidence only.

#### Scenario: D-07 and D-08 promotion plan is registered without status change

- **WHEN** the PingAn trading implemented promotion plan is registered
- **THEN** D-07 and D-08 SHALL continue to use `[部分实现]`
- **AND** their evidence SHALL cite the promotion plan
- **AND** their boundary SHALL list the remaining evidence gates before `[已实现]`.

#### Scenario: Catalog-only evidence is insufficient for implemented status

- **WHEN** D-07 or D-08 evidence only contains catalog validate, catalog plan, catalog preview, or bundle summary output
- **THEN** the FUNCTION_TREE validator and registry policy SHALL treat that evidence as read-only discovery/registration evidence
- **AND** the node boundary SHALL NOT claim broker readiness, trading safety approval, production readiness, or implemented status from that evidence alone.

#### Scenario: Preflight provider and safety gate evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites readonly PingAn `promotion_gate_status` from `trade preflight`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the gate status
- **AND** the boundary SHALL state that desktop lifecycle, audit, and acceptance gates remain before `[已实现]`.

#### Scenario: Dialog lifecycle gate evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites readonly PingAn `desktop_lifecycle_gate_status` from `trade dialog-readiness`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the gate status
- **AND** the boundary SHALL state that exception popup handling, retry policy, audit evidence, and acceptance evidence remain before `[已实现]`.

#### Scenario: Per-result audit gate evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites PingAn `trade_audit_gate_status` from finalized trade results
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the gate status
- **AND** the boundary SHALL state that complete success/failure/rejection/exception coverage and acceptance evidence remain before `[已实现]`.

#### Scenario: Explicit exception audit outcome evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites PingAn `trade_audit_gate_status.covered_audit_status=exception` from an explicitly exception-marked finalized result
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the exception audit outcome status
- **AND** the boundary SHALL state that exception popup handling, retry policy, and live/manual acceptance remain before `[已实现]`.

#### Scenario: Failed audit classification evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites PingAn `trade_audit_gate_status.audit_status_classification.source=generic_execution_failure`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the failed audit classification status
- **AND** the boundary SHALL state that generic failed outcome classification does not prove retry, recovery, broker readiness, or live/manual acceptance.

#### Scenario: Acceptance outcome coverage evidence is registered as partial evidence

- **WHEN** D-07 or D-08 evidence cites PingAn `acceptance_outcome_coverage_status` from trade audit reports
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the coverage status
- **AND** the boundary SHALL state that report coverage is read-only and that missing automated outcome statuses plus live/manual acceptance evidence remain before `[已实现]`.

### Requirement: PingAn automated outcome coverage completion SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn automated outcome coverage completion as read-only report evidence without using it to promote D-07 or D-08 to `[已实现]`.

#### Scenario: Automated outcome coverage completion is registered without status change

- **WHEN** D-07 or D-08 evidence cites `acceptance_outcome_coverage_status.automated_outcome_coverage_complete=true`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the completion flag
- **AND** the boundary SHALL state that live/manual acceptance remains required before `[已实现]`.

### Requirement: PingAn exception popup readiness evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn exception popup readiness as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Exception popup readiness is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.dialog_checks.exception_popup_lookup`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the lookup status
- **AND** the boundary SHALL state that actual exception popup handling, retry/recovery, and live/manual acceptance remain required before `[已实现]`.
