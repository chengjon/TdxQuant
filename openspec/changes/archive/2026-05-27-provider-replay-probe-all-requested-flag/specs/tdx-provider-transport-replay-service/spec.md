## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose all-requested coverage

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.all_probes_requested` derived from the existing probe request coverage calculation.

#### Scenario: No-probe request reports false

- **WHEN** provider replay status has no requested probes
- **THEN** `runtime.probe_summary.all_probes_requested` MUST be `false`
- **AND** the field MUST remain consistent with `outcome_summary.all_probes_requested`

#### Scenario: Partial probe request reports false

- **WHEN** provider replay status has configured probes that were not requested
- **THEN** `runtime.probe_summary.all_probes_requested` MUST be `false`
- **AND** the field MUST remain consistent with `requested_count < total_count`

#### Scenario: Complete probe request reports true

- **WHEN** provider replay status requested every configured probe
- **THEN** `runtime.probe_summary.all_probes_requested` MUST be `true`
- **AND** the field MUST remain consistent with `requested_count == total_count`

#### Scenario: All-requested coverage remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.all_probes_requested`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint health, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed
