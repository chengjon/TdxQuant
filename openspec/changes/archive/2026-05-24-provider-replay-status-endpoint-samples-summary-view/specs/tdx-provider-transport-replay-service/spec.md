# tdx-provider-transport-replay-service Delta

## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose bounded endpoint samples

The provider replay status summary view SHALL include bounded read-only endpoint samples derived from the detailed `capabilities.endpoints` list without exposing the complete endpoint list or changing replay service lifecycle/probe behavior.

#### Scenario: Caller requests provider replay status summary endpoint samples

- **WHEN** a caller runs `provider-replay status --config <path> --view summary`
- **THEN** `summary_view.capabilities` MUST include `endpoint_samples`
- **AND** `summary_view.capabilities` MUST include `endpoint_sample_limit`
- **AND** `summary_view.capabilities` MUST include `endpoint_sample_truncated`
- **AND** `summary_view.capabilities` MUST continue to include `endpoint_count`
- **AND** `summary_view.capabilities` MUST NOT include the full `endpoints` list
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, or probe unless explicit probe flags are provided

