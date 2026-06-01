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

### Requirement: PingAn process/window observation evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn process/window observation as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Process/window observation is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.observed_process_window_ownership`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the observation status
- **AND** the boundary SHALL state that real lifecycle control, process ownership, statefile locking, restart/backoff, and live/manual acceptance remain required before `[已实现]`.

### Requirement: PingAn retry policy status evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn retry policy status as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Retry policy status is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.retry_policy_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the status
- **AND** the boundary SHALL state that executable retry/backoff/recovery/resubmission and live/manual acceptance remain required before `[已实现]`.

### Requirement: PingAn exception popup handling status evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn exception popup handling status as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Exception popup handling status is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.exception_popup_handling_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the status
- **AND** the boundary SHALL state that executable popup handling, control clicks, recovery, retry/resubmission, and live/manual acceptance remain required before `[已实现]`.

### Requirement: PingAn statefile lock status evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn statefile lock status as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Statefile lock status is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.statefile_lock_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the status
- **AND** the boundary SHALL state that executable statefile locking, owner token writes, lifecycle control, process ownership, restart/backoff, and live/manual acceptance remain required before `[已实现]`.

### Requirement: PingAn lifecycle control status evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn lifecycle control status as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Lifecycle control status is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.lifecycle_control_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the status
- **AND** the boundary SHALL state that executable process lifecycle control, supervisor ownership, PID ownership, restart/backoff, statefile locking, and live/manual acceptance remain required before `[已实现]`.

### Requirement: PingAn lifecycle owner lock evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn lifecycle owner lock evidence as a concrete local lifecycle artifact while preserving D-07/D-08 partial status.

#### Scenario: Lifecycle owner lock evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites PingAn lifecycle owner lock acquire/release behavior
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the owner lock behavior
- **AND** the boundary SHALL state that executable process lifecycle control, supervisor ownership, PID ownership, restart/backoff, broker readiness, and live/manual acceptance remain required before `[已实现]`.

### Requirement: PingAn owner PID validation evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn owner PID validation evidence as local lifecycle ownership diagnostics while preserving D-07/D-08 partial status.

#### Scenario: Owner PID validation evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites PingAn lifecycle owner PID validation
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the owner PID validation
- **AND** the boundary SHALL state that owner PID liveness does not claim real PingAn desktop process ownership, supervisor control, restart/backoff, broker readiness, or live/manual acceptance.

### Requirement: PingAn lifecycle owner lock CLI evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite the PingAn lifecycle owner lock CLI entry as partial lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Lifecycle owner lock CLI evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites `trade lifecycle-owner-lock`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the CLI entry
- **AND** the boundary SHALL state that CLI access to owner lock statefiles does not provide real process lifecycle control, broker readiness, or live/manual acceptance.

### Requirement: PingAn preflight owner lock status evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn preflight lifecycle owner lock status as partial lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Preflight owner lock status evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites `promotion_gate_status.lifecycle_owner_lock_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the preflight owner lock status gate
- **AND** the boundary SHALL state that preflight owner lock status is read-only local statefile evidence and does not provide real process lifecycle control, broker readiness, or live/manual acceptance.

### Requirement: PingAn required owner lock preflight gate evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn required owner lock preflight gate evidence as partial safety/lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Required owner lock preflight gate is registered without status change

- **WHEN** D-07 or D-08 evidence cites `lifecycle_owner_lock_status.required=true`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the required owner lock preflight gate
- **AND** the boundary SHALL state that the gate is read-only local statefile safety evidence and does not provide real process lifecycle control, broker readiness, or live/manual acceptance.

### Requirement: PingAn execution owner-lock guard evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn execution owner-lock guard evidence as partial safety/lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Execution owner-lock guard evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites `trade_safety.risk_gate.lifecycle_owner_lock_required_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the execution owner-lock guard
- **AND** the boundary SHALL state that the guard is opt-in local statefile safety evidence and does not provide real process lifecycle control, broker readiness, production readiness, or live/manual acceptance.

### Requirement: PingAn task execution owner-lock guard evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite task-level PingAn owner-lock execution guard coverage as partial safety/lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Task owner-lock guard evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites task trade owner-lock guard forwarding
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce task-level owner-lock guard forwarding
- **AND** the boundary SHALL state that the task layer only forwards an opt-in local guard and does not acquire/release locks, write lifecycle statefile/lock artifacts directly, control PingAn processes, prove broker readiness, or provide live/manual acceptance.

### Requirement: PingAn task-run owner-lock guard evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite task-run preset/override owner-lock guard forwarding as partial D-07/D-08 safety evidence only.

#### Scenario: Task-run guard evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites `task run` owner-lock guard preset/override forwarding
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce task-run guard forwarding
- **AND** the boundary SHALL state that the task-run layer only resolves and forwards an opt-in local guard and does not acquire/release locks, write lifecycle statefile/lock artifacts directly, control PingAn processes, prove broker readiness, or provide live/manual acceptance.

### Requirement: PingAn guarded trade owner-lock guard evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite guarded trade-buy owner-lock guard forwarding as partial D-07 safety evidence only.

#### Scenario: Guarded owner-lock evidence is registered without status change

- **WHEN** D-07 evidence cites guarded trade-buy owner-lock guard forwarding
- **THEN** D-07 SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce guarded owner-lock guard forwarding
- **AND** the boundary SHALL state that guarded trade-buy only forwards an opt-in local guard and does not acquire/release locks, write lifecycle statefile/lock artifacts directly, control PingAn processes, prove broker readiness, or provide live/manual acceptance.

### Requirement: D-07 confirm-current owner-lock guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register confirm-current owner-lock guard coverage as D-07 partial safety evidence without promoting PingAn trading to implemented status.

#### Scenario: D-07 registers confirm-current owner-lock guard without status promotion
- **WHEN** D-07 cites `pingan-confirm-current-owner-lock-guard`
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade confirm-current --require-lifecycle-owner-lock`, `task trade-confirm-current --require-lifecycle-owner-lock`, and `TdxTradeManager.pingan.confirm_current`
- **AND** the row boundary MUST state that this is opt-in owner-lock guard evaluation only and does not prove lifecycle control, broker readiness, live/manual acceptance, or production trading readiness.

### Requirement: D-07 submit-ready owner-lock guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register submit-ready owner-lock guard coverage as D-07 partial safety evidence without promoting PingAn trading to implemented status.

#### Scenario: D-07 registers submit-ready owner-lock guard without status promotion
- **WHEN** D-07 cites `pingan-submit-ready-owner-lock-guard`
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade submit-ready --require-lifecycle-owner-lock`, `task trade-submit-ready --require-lifecycle-owner-lock`, and `TdxTradeManager.pingan.submit_ready`
- **AND** the row boundary MUST state that this is opt-in owner-lock guard evaluation only and does not prove lifecycle control, broker readiness, live/manual acceptance, or production trading readiness.

### Requirement: D-07/D-08 exception popup control evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register PingAn exception popup manual close control as D-07/D-08 partial desktop lifecycle evidence without promoting either node to implemented status.

#### Scenario: Registry cites exception popup manual close control without status promotion
- **WHEN** D-07 or D-08 cites `pingan-exception-popup-manual-close-control`
- **THEN** the row MUST remain `[部分实现]`
- **AND** the row MUST cite `TdxTradeManager.pingan.exception_popup`, `trade exception-popup --action inspect`, and `trade exception-popup --action close --confirm-close`
- **AND** the row boundary MUST state that the control is explicit exception-popup inspect/close only and does not retry, recover, resubmit, prove broker readiness/live acceptance, or complete workflow/lifecycle governance.

### Requirement: D-07 confirm-current broker readiness guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register confirm-current broker readiness guard coverage as D-07 partial safety evidence without promoting PingAn trading to implemented status.

#### Scenario: D-07 registers confirm-current broker readiness guard without status promotion
- **WHEN** D-07 cites `pingan-confirm-current-broker-readiness-guard`
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade confirm-current --require-broker-readiness`, `task trade-confirm-current --require-broker-readiness`, and `TdxTradeManager.pingan.confirm_current`
- **AND** the row boundary MUST state that this is opt-in broker runtime health guard evaluation only and does not prove lifecycle control, retry/backoff/recovery, live/manual acceptance, or production trading readiness.

### Requirement: D-07 buy/sell broker readiness guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register buy/sell broker readiness guard coverage as D-07 partial safety evidence without promoting PingAn trading to implemented status.

#### Scenario: D-07 registers buy/sell broker readiness guard without status promotion
- **WHEN** D-07 cites `pingan-buy-sell-broker-readiness-guard`
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade buy --require-broker-readiness`, `trade sell --require-broker-readiness`, `task trade-buy --require-broker-readiness`, `task trade-sell --require-broker-readiness`, and `TdxTradeManager.pingan.buy/sell`
- **AND** the row boundary MUST state that this is opt-in broker runtime health guard evaluation only and does not prove lifecycle control, retry/backoff/recovery, live/manual acceptance, or production trading readiness.

### Requirement: D-08 submit-once broker readiness guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register submit-once broker readiness guard coverage as D-08 partial safety evidence without promoting PingAn submit-once to implemented status.

#### Scenario: D-08 registers submit-once broker readiness guard without status promotion
- **WHEN** D-08 cites `pingan-submit-once-broker-readiness-guard`
- **THEN** D-08 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade submit-once --require-broker-readiness`, `task trade-submit-once --require-broker-readiness`, and `TdxTradeManager.pingan.buy_submit_once/sell_submit_once`
- **AND** the row boundary MUST state that this is opt-in broker runtime health guard evaluation only and does not prove lifecycle control, retry/backoff/recovery, live/manual acceptance, or production trading readiness.

### Requirement: FUNCTION_TREE SHALL register PingAn lifecycle supervisor control without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn lifecycle supervisor control evidence on D-07 and D-08 while preserving accurate feature status.

#### Scenario: D-07 and D-08 register supervisor evidence as partial lifecycle control

- **WHEN** PingAn lifecycle supervisor tick/run manager methods and CLI entrypoints are added
- **THEN** D-07 and D-08 MUST include evidence for `pingan-lifecycle-supervisor-control`
- **AND** D-07 and D-08 MUST include evidence for `TdxTradeManager.pingan.lifecycle_supervisor_tick`
- **AND** D-07 and D-08 MUST include evidence for `trade lifecycle-supervisor-tick`
- **AND** D-07 and D-08 MUST remain `[部分实现]` unless all remaining live/manual acceptance and desktop lifecycle gates are independently satisfied.

#### Scenario: FUNCTION_TREE boundary prevents lifecycle readiness overclaiming

- **WHEN** D-07 or D-08 mention lifecycle supervisor evidence
- **THEN** the boundary MUST state that the evidence is local statefile-backed lifecycle control
- **AND** the boundary MUST state that it does not submit orders, execute catalog/task/report/bundle workflows, own/kill/start the real PingAn process, or prove production trading readiness.

### Requirement: FUNCTION_TREE SHALL register PingAn process lifecycle control without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn process lifecycle control evidence on D-07 and D-08 while preserving accurate partial status.

#### Scenario: D-07 and D-08 register process lifecycle evidence

- **WHEN** PingAn process lifecycle manager and CLI entrypoints are added
- **THEN** D-07 and D-08 MUST include evidence for `pingan-process-lifecycle-control`
- **AND** D-07 and D-08 MUST include evidence for `TdxTradeManager.pingan.lifecycle_process`
- **AND** D-07 and D-08 MUST include evidence for `trade lifecycle-process`
- **AND** D-07 and D-08 MUST remain `[部分实现]` unless all remaining live/manual acceptance and trading readiness gates are independently satisfied.

#### Scenario: FUNCTION_TREE boundary prevents readiness overclaiming

- **WHEN** D-07 or D-08 mention process lifecycle control evidence
- **THEN** the boundary MUST state that this controls only explicit owner-locked local process start/stop/restart for recorded PIDs
- **AND** the boundary MUST state that it does not submit orders, execute catalog/task/report/bundle workflows, prove broker readiness, prove UI login readiness, or provide production trading readiness.

### Requirement: FUNCTION_TREE SHALL register PingAn supervisor process restart integration without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn supervisor process restart integration evidence on D-07 and D-08 while preserving accurate partial status.

#### Scenario: D-07 and D-08 register supervisor process restart evidence

- **WHEN** supervisor tick/run can opt into recorded-PID process restart
- **THEN** D-07 and D-08 MUST include evidence for `pingan-supervisor-process-restart-control`
- **AND** D-07 and D-08 MUST include evidence for `process_restart_enabled`
- **AND** D-07 and D-08 MUST include evidence for `trade lifecycle-supervisor-tick --process-restart`
- **AND** D-07 and D-08 MUST remain `[部分实现]`.

#### Scenario: FUNCTION_TREE boundary prevents supervisor restart overclaiming

- **WHEN** D-07 or D-08 mention supervisor process restart evidence
- **THEN** the boundary MUST state that process restart is explicit opt-in and delegated to recorded-PID lifecycle process guards
- **AND** the boundary MUST state that it does not submit orders, execute catalog/task/report/bundle workflows, prove broker readiness, prove UI login readiness, or provide production trading readiness.

### Requirement: FUNCTION_TREE SHALL register PingAn post-restart readiness summary without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn supervisor post-restart readiness summary evidence on D-07 and D-08 while preserving accurate partial status.

#### Scenario: D-07 and D-08 register post-restart summary evidence

- **WHEN** supervisor tick/run can opt into post-restart broker health recheck
- **THEN** D-07 and D-08 MUST include evidence for `pingan-supervisor-restart-readiness-summary`
- **AND** D-07 and D-08 MUST include evidence for `process_restart_recheck_enabled`
- **AND** D-07 and D-08 MUST include evidence for `lifecycle_recovery_status`
- **AND** D-07 and D-08 MUST remain `[部分实现]`.

#### Scenario: FUNCTION_TREE boundary prevents readiness overclaiming

- **WHEN** D-07 or D-08 mention post-restart readiness summary evidence
- **THEN** the boundary MUST state that post-restart health recheck is immediate lifecycle evidence only
- **AND** the boundary MUST state that it does not prove order readiness, UI login readiness, broker production readiness, or live/manual acceptance.

### Requirement: FUNCTION_TREE SHALL register PingAn live manual acceptance evidence without promotion

`FUNCTION_TREE.md` SHALL register the live/manual acceptance evidence slice for D-07 and D-08 while preserving their `[部分实现]` status.

#### Scenario: D-07 and D-08 register live manual acceptance evidence

- **WHEN** trade audit reports can summarize optional live/manual acceptance evidence
- **THEN** D-07 and D-08 SHALL cite `pingan-live-manual-acceptance-evidence`
- **AND** D-07 and D-08 SHALL cite `live_manual_acceptance_complete`
- **AND** D-07 and D-08 SHALL cite `acceptance_complete`
- **AND** D-07 and D-08 SHALL remain `[部分实现]`.

#### Scenario: FUNCTION_TREE boundary prevents manual acceptance overclaiming

- **WHEN** D-07 or D-08 evidence cites live/manual acceptance report evidence
- **THEN** the boundary SHALL state that the evidence is read-only report evidence
- **AND** the boundary SHALL state that it does not execute trades or workflows
- **AND** the boundary SHALL state that it does not prove broker production readiness, UI login readiness, order safety, or implemented status.

### Requirement: FUNCTION_TREE SHALL register PingAn promotion readiness rollup without promotion

`FUNCTION_TREE.md` SHALL register PingAn promotion readiness rollup evidence for D-07 and D-08 while preserving their `[部分实现]` status.

#### Scenario: D-07 and D-08 cite rollup evidence

- **WHEN** the promotion readiness rollup task exists
- **THEN** D-07 and D-08 SHALL cite `pingan-promotion-readiness-rollup`
- **AND** D-07 and D-08 SHALL cite `promotion_readiness_rollup`
- **AND** D-07 and D-08 SHALL cite `completed_gates` and `incomplete_gates`
- **AND** D-07 and D-08 SHALL remain `[部分实现]`.

#### Scenario: FUNCTION_TREE boundary prevents rollup overclaiming

- **WHEN** D-07 or D-08 evidence cites the rollup
- **THEN** the boundary SHALL state that the rollup is read-only evidence aggregation
- **AND** the boundary SHALL state that it does not execute broker/desktop/trade/report/catalog workflows
- **AND** the boundary SHALL state that it does not by itself prove production readiness or implemented status.

### Requirement: FUNCTION_TREE SHALL record evidence freshness guarding without status promotion

FUNCTION_TREE SHALL register the PingAn promotion readiness freshness gate as a read-only evidence guard and SHALL NOT treat it as implemented trading capability.

#### Scenario: Freshness guard is visible but non-promoting

- **WHEN** the freshness gate is added to the tree evidence
- **THEN** the D-07/D-08 rows SHALL keep their `[部分实现]` status
- **AND** their boundary text SHALL mention stale evidence rejection
- **AND** the tree SHALL not imply promotion to `[已实现]`.

### Requirement: FUNCTION_TREE SHALL register promotion readiness artifact output without status promotion

FUNCTION_TREE SHALL record the JSON artifact output as evidence capture for D-07/D-08 and SHALL keep those nodes `[部分实现]`.

#### Scenario: Artifact output is registered as evidence-only

- **WHEN** the artifact output is added to D-07/D-08
- **THEN** the tree SHALL include the task option and output metadata
- **AND** the boundary SHALL state that artifact writing does not refresh evidence or execute workflows
- **AND** D-07/D-08 SHALL remain `[部分实现]`.

### Requirement: FUNCTION_TREE SHALL register promotion readiness manifest input without status promotion

FUNCTION_TREE SHALL record the evidence manifest input as a reproducibility aid for D-07/D-08 while preserving `[部分实现]` status.

#### Scenario: Manifest input is registered as read-only evidence selection

- **WHEN** the manifest input is added to D-07/D-08
- **THEN** the tree SHALL include the manifest path option and manifest metadata
- **AND** the boundary SHALL state that manifests do not refresh evidence or execute workflows
- **AND** D-07/D-08 SHALL remain `[部分实现]`.

### Requirement: FUNCTION_TREE SHALL register PingAn readiness manifest sample evidence without status promotion

`FUNCTION_TREE.md` SHALL cite the PingAn readiness manifest sample and catalog/task registration as partial evidence only.

#### Scenario: D-07 and D-08 cite manifest sample registration while remaining partial

- **GIVEN** D-07 and D-08 describe PingAn desktop trading readiness
- **WHEN** the PingAn readiness manifest sample registry is added
- **THEN** D-07 and D-08 SHALL remain `[部分实现]`
- **AND** their evidence SHALL cite `runtime/pingan/promotion-readiness-manifest.example.json`
- **AND** their evidence SHALL cite `plan-pingan-promotion-readiness`
- **AND** their evidence SHALL cite the OpenSpec change `pingan-promotion-readiness-manifest-sample-registry`
- **AND** their boundary SHALL say the entry is read-only discovery/registration evidence
- **AND** their boundary SHALL say the sample does not execute broker, desktop, trade, report, task, or bundle workflows
- **AND** their boundary SHALL say the sample does not prove production readiness or implemented status.

### Requirement: FUNCTION_TREE SHALL cite PingAn promotion decision as partial mainline evidence

`FUNCTION_TREE.md` SHALL register the implemented-status promotion decision as mainline evidence for D-07/D-08 while keeping both nodes partial until a later explicit status-transition change is completed.

#### Scenario: D-07 and D-08 remain partial after promotion-decision implementation

- **GIVEN** the PingAn implemented-status promotion decision exists
- **WHEN** D-07 and D-08 cite it as evidence
- **THEN** both nodes SHALL remain `[部分实现]`
- **AND** both nodes SHALL cite `implemented_status_promotion_decision`
- **AND** both nodes SHALL cite `eligible_for_review`
- **AND** both nodes SHALL cite `blocked_reasons`
- **AND** both nodes SHALL cite the OpenSpec change `pingan-implemented-status-promotion-decision`
- **AND** both node boundaries SHALL say the decision is read-only and fail-closed
- **AND** both node boundaries SHALL say it does not execute PingAn workflows
- **AND** both node boundaries SHALL say it does not automatically edit FUNCTION_TREE status.

### Requirement: FUNCTION_TREE SHALL register PingAn evidence provenance gate as partial evidence

`FUNCTION_TREE.md` SHALL register source evidence schema-contract validation as mainline D-07/D-08 evidence while keeping both nodes partial.

#### Scenario: D-07 and D-08 cite evidence contract without status promotion

- **GIVEN** PingAn promotion readiness rollup exposes `evidence_contract_status`
- **WHEN** D-07 and D-08 cite the provenance gate
- **THEN** both nodes SHALL remain `[部分实现]`
- **AND** both nodes SHALL cite `evidence_contract_status`
- **AND** both nodes SHALL cite `unverified_evidence_contract`
- **AND** both nodes SHALL cite `pingan-evidence-provenance-promotion-gate`
- **AND** both node boundaries SHALL say schema-contract validation is read-only
- **AND** both node boundaries SHALL say schema-contract validation does not prove production readiness or implemented status.

### Requirement: FUNCTION_TREE SHALL register PingAn artifact provenance gate as partial evidence

`FUNCTION_TREE.md` SHALL register artifact provenance validation as mainline D-07/D-08 evidence while keeping both nodes partial.

#### Scenario: D-07 and D-08 cite artifact provenance gate without status promotion

- **GIVEN** PingAn promotion readiness rollup exposes `artifact_provenance_status`
- **WHEN** D-07 and D-08 cite the provenance gate
- **THEN** both nodes SHALL remain `[部分实现]`
- **AND** both nodes SHALL cite `artifact_provenance_status`
- **AND** both nodes SHALL cite `unverified_artifact_provenance`
- **AND** both nodes SHALL cite `pingan-artifact-provenance-promotion-gate`
- **AND** both node boundaries SHALL say artifact provenance validation is read-only
- **AND** both node boundaries SHALL say artifact provenance does not prove production readiness or implemented status.

### Requirement: FUNCTION_TREE SHALL register PingAn readiness evidence producer provenance without status promotion

`FUNCTION_TREE.md` SHALL record that D-07/D-08 include producer-emitted artifact provenance for PingAn readiness evidence while keeping both nodes `[部分实现]`.

#### Scenario: Producer provenance is registered as partial implementation evidence

- **WHEN** `FUNCTION_TREE.md` describes D-07 and D-08
- **THEN** both rows SHALL mention `pingan-readiness-evidence-producer-provenance`
- **AND** both rows SHALL mention the producer provenance fields for preflight, dialog readiness, and acceptance coverage
- **AND** both rows SHALL keep status `[部分实现]`
- **AND** both rows SHALL state that producer provenance does not execute PingAn workflows, does not prove production readiness, and does not prove implemented status.

### Requirement: FUNCTION_TREE SHALL register PingAn manual acceptance recorder without status promotion

`FUNCTION_TREE.md` SHALL record the PingAn live/manual acceptance recorder as D-07/D-08 partial implementation evidence while keeping both nodes `[部分实现]`.

#### Scenario: Recorder is registered as controlled manual evidence capture

- **WHEN** `FUNCTION_TREE.md` describes D-07 and D-08
- **THEN** both rows SHALL mention `pingan-live-manual-acceptance-recorder`
- **AND** both rows SHALL mention `task pingan-live-manual-acceptance`
- **AND** both rows SHALL mention `tdx.desktop_trade.pingan_live_manual_acceptance.v1`
- **AND** both rows SHALL keep status `[部分实现]`
- **AND** both rows SHALL state that this recorder does not execute PingAn workflows, does not prove production readiness, and does not prove implemented status.

### Requirement: FUNCTION_TREE SHALL register live/manual acceptance provenance rollup without promotion

`FUNCTION_TREE.md` SHALL record that D-07 and D-08 include live/manual acceptance recorder provenance validation as partial promotion-readiness evidence only.

#### Scenario: D-07 and D-08 register live/manual recorder provenance while staying partial

- **WHEN** D-07 or D-08 cites `pingan-live-manual-acceptance-provenance-rollup`
- **THEN** the node status SHALL remain `[部分实现]`
- **AND** evidence SHALL mention `live_manual_acceptance_provenance_status`
- **AND** evidence SHALL mention `unverified_live_manual_acceptance_artifact_provenance`
- **AND** the boundary SHALL state that this is read-only recorder provenance validation and does not execute PingAn workflows, submit orders, prove production readiness, or promote implemented status.

### Requirement: FUNCTION_TREE SHALL register PingAn implemented-status review packet without promotion

`FUNCTION_TREE.md` SHALL record that D-07 and D-08 include an implemented-status review packet as partial status-review evidence only.

#### Scenario: D-07 and D-08 register review packet while staying partial

- **WHEN** D-07 or D-08 cites `pingan-implemented-status-review-packet`
- **THEN** the node status SHALL remain `[部分实现]`
- **AND** evidence SHALL mention `implemented_status_review_packet`
- **AND** evidence SHALL mention `ready_for_manual_review`
- **AND** the boundary SHALL state that the packet is a read-only manual status review input and does not execute PingAn workflows, submit orders, prove production readiness, or promote implemented status.

### Requirement: FUNCTION_TREE SHALL register PingAn implemented-status review result recorder without promotion

`FUNCTION_TREE.md` SHALL record the PingAn implemented-status review result recorder as D-07/D-08 partial manual review evidence while keeping both nodes `[部分实现]`.

#### Scenario: D-07 and D-08 register review result recorder while staying partial

- **WHEN** D-07 or D-08 cites `pingan-implemented-status-review-result-recorder`
- **THEN** the node status SHALL remain `[部分实现]`
- **AND** evidence SHALL mention `implemented_status_review_result`
- **AND** evidence SHALL mention `approve/reject/defer`
- **AND** evidence SHALL mention `manual_status_review_result_record`
- **AND** the boundary SHALL state that this recorder does not execute PingAn workflows, does not automatically modify FUNCTION_TREE status, does not prove production readiness, and does not prove implemented status.
