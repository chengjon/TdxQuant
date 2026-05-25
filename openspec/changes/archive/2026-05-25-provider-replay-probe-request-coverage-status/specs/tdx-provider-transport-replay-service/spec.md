## ADDED Requirements

### Requirement: Provider replay status SHALL summarize probe request coverage

Provider replay status SHALL include additive `runtime.probe_summary.request_coverage_status` derived from existing probe counts without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No probes requested

- **WHEN** provider replay status is built without any explicit probe result
- **THEN** `runtime.probe_summary.request_coverage_status` MUST be `none`
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Some probes requested

- **WHEN** provider replay status is built with at least one but not all known probe results
- **THEN** `runtime.probe_summary.request_coverage_status` MUST be `partial`
- **AND** the value MUST NOT imply health or readiness

#### Scenario: All probes requested

- **WHEN** provider replay status is built with all known probe results
- **THEN** `runtime.probe_summary.request_coverage_status` MUST be `complete`
- **AND** the value MUST NOT imply all probes are healthy

#### Scenario: CLI summary preserves request coverage status

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.request_coverage_status`
- **AND** the summary payload MUST remain a read-only projection
