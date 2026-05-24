# tdx-provider-transport-replay-service Delta

## ADDED Requirements

### Requirement: Provider replay status SHALL summarize probe error codes

Provider replay status SHALL expose additive `runtime.probe_summary.error_code_counts` derived from existing normalized probe objects, without starting sockets, managing daemon lifecycle, changing probe endpoints, or exposing secrets.

#### Scenario: No requested probe errors produce empty counts

- **WHEN** a caller builds provider replay status without unhealthy probe error codes
- **THEN** `runtime.probe_summary.error_code_counts` MUST be an empty object
- **AND** existing probe status counts and target lists MUST remain unchanged

#### Scenario: Unhealthy probe errors are counted by code

- **WHEN** a caller builds provider replay status with one or more probe objects that include `error_code`
- **THEN** `runtime.probe_summary.error_code_counts` MUST count each error code
- **AND** the probe summary status MUST remain derived from requested and unhealthy probes
- **AND** the status operation MUST remain read-only and MUST NOT manage daemon lifecycle

#### Scenario: CLI summary view preserves probe error-code counts

- **WHEN** a caller runs `provider-replay status --view summary`
- **AND** the underlying runtime probe summary includes `error_code_counts`
- **THEN** `summary_view.probe_summary.error_code_counts` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST remain a read-only projection
