## ADDED Requirements

### Requirement: Provider replay status SHALL expose a primary failed probe hint

Provider replay status SHALL include additive `runtime.probe_summary.primary_failed_probe` derived from the existing failed probe list without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No failed probes

- **WHEN** provider replay status is built without failed probes
- **THEN** `runtime.probe_summary.primary_failed_probe` MUST be `null`
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Failed probes exist

- **WHEN** provider replay status is built with one or more failed probes
- **THEN** `runtime.probe_summary.primary_failed_probe` MUST equal the first item in `runtime.probe_summary.failed`
- **AND** the value MUST NOT imply recovery, health, or readiness

#### Scenario: CLI summary preserves primary failed probe

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.primary_failed_probe`
- **AND** the summary payload MUST remain a read-only projection
