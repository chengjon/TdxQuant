## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose problem probe presence

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.has_problem_probe` derived only from existing normalized primary problem probe metadata.

#### Scenario: No problem probe reports false

- **WHEN** provider replay status has no primary problem probe
- **THEN** top-level `runtime.probe_summary.has_problem_probe` MUST be `false`
- **AND** the field MUST remain consistent with `primary_problem_probe is None`

#### Scenario: Problem probe reports true

- **WHEN** provider replay status has a primary problem probe
- **THEN** top-level `runtime.probe_summary.has_problem_probe` MUST be `true`
- **AND** the field MUST remain consistent with `primary_problem_probe is not None`

#### Scenario: Problem probe presence remains advisory

- **WHEN** provider replay status exposes top-level `runtime.probe_summary.has_problem_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed
