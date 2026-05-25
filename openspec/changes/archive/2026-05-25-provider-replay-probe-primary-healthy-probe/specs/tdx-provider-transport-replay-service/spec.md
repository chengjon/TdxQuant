## ADDED Requirements

### Requirement: Provider replay status SHALL expose a primary healthy probe hint

Provider replay status SHALL include additive `runtime.probe_summary.primary_healthy_probe` derived from the existing healthy probe list without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No healthy probes

- **WHEN** provider replay status is built without healthy probes
- **THEN** `runtime.probe_summary.primary_healthy_probe` MUST be `null`
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Healthy probes exist

- **WHEN** provider replay status is built with one or more healthy probes
- **THEN** `runtime.probe_summary.primary_healthy_probe` MUST equal the first item in `runtime.probe_summary.healthy`
- **AND** the value MUST NOT imply full service health, readiness, or endpoint coverage

#### Scenario: CLI summary preserves primary healthy probe

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.primary_healthy_probe`
- **AND** the summary payload MUST remain a read-only projection
