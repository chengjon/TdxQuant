# tdx-provider-transport-replay-service Delta

## ADDED Requirements

### Requirement: Provider replay status SHALL expose bounded probe error samples

Provider replay status SHALL include additive `runtime.probe_summary.error_samples`, `error_sample_limit`, and `error_sample_truncated` fields derived from existing normalized probe objects, without starting sockets, managing daemon lifecycle, changing probe endpoints, or exposing secrets.

#### Scenario: No probe errors produce empty samples

- **WHEN** a caller builds provider replay status without unhealthy probe errors
- **THEN** `runtime.probe_summary.error_samples` MUST be an empty list
- **AND** `runtime.probe_summary.error_sample_limit` MUST identify the sample cap
- **AND** `runtime.probe_summary.error_sample_truncated` MUST be `false`

#### Scenario: Probe errors produce compact bounded samples

- **WHEN** a caller builds provider replay status with unhealthy or error-classified probe objects
- **THEN** `runtime.probe_summary.error_samples` MUST include compact probe metadata
- **AND** each sample MUST include the probe key and normalized status
- **AND** samples MAY include `error_code` and `http_status` when present
- **AND** the sample list MUST NOT expose secret tokens, allowlist members, or full raw probe payloads

#### Scenario: CLI summary view preserves probe error samples

- **WHEN** a caller runs `provider-replay status --view summary`
- **AND** the underlying runtime probe summary includes `error_samples`
- **THEN** `summary_view.probe_summary.error_samples` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST remain a read-only projection
