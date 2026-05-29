## ADDED Requirements

### Requirement: Subscription watch-status SHALL expose read-only operator runbook view

HTTP and CLI watch-status commands SHALL expose an opt-in `runbook` view derived from existing summary and diagnostics data without changing lifecycle behavior.

#### Scenario: CLI runbook view projects operator checklist

- **WHEN** a caller runs `bridge watch-status --view runbook`
- **THEN** the command MUST emit a compact payload with `result.mode` equal to `runbook`
- **AND** the payload MUST include a top-level `result.runbook` object
- **AND** the runbook MUST include `schema_version`, `decision`, `check_count`, `blocking_check_count`, `manual_review_required`, `checks`, and `boundary`
- **AND** the command MUST NOT call restart preflight, start, stop, restart, supervisor tick, supervisor run, daemon control, probe, signal processes, schedule retry, or mutate provider state.

#### Scenario: HTTP runbook view projects operator checklist

- **WHEN** a caller requests `GET /bridge/v1/watch/status?view=runbook`
- **THEN** the HTTP response MUST include `result.mode` equal to `runbook`
- **AND** the response MUST include a top-level `result.runbook` object
- **AND** the runbook MUST be derived from existing summary/diagnostics projections
- **AND** the response MUST NOT expose raw statefile content, owner token, daemon command, daemon settings, raw control payload, raw watch payload, or full detailed payload through this projection.

#### Scenario: Operator runbook remains read-only

- **WHEN** the runbook view is produced
- **THEN** it MUST NOT prove live provider availability, broker readiness, trading readiness, PID ownership beyond existing local evidence, production lifecycle health, or complete long-run governance
- **AND** it MUST NOT create or execute a workflow, task, report, trade, catalog step, restart policy, or daemon policy.
