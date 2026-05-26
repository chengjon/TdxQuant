## ADDED Requirements

### Requirement: Provider replay status SHALL expose a primary not-requested probe hint

Provider replay status SHALL include additive `runtime.probe_summary.primary_not_requested_probe` derived from the existing not-requested probe list without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: All probes requested

- **WHEN** provider replay status is built with every supported probe requested
- **THEN** `runtime.probe_summary.primary_not_requested_probe` MUST be `null`
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Not-requested probes exist

- **WHEN** provider replay status is built with one or more not-requested probes
- **THEN** `runtime.probe_summary.primary_not_requested_probe` MUST equal the first item in `runtime.probe_summary.not_requested`
- **AND** the value MUST NOT imply that the target has been probed, failed, or is unavailable

#### Scenario: CLI summary preserves primary not-requested probe

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.primary_not_requested_probe`
- **AND** the summary payload MUST remain a read-only projection
