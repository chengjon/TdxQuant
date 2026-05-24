# tdx-provider-transport-replay-service Delta

## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose endpoint family counts

The provider replay status summary view SHALL include compact endpoint family counts derived from the detailed `capabilities.endpoints` list without exposing the complete endpoint list or changing replay service lifecycle/probe behavior.

#### Scenario: Caller requests provider replay status summary endpoint family counts

- **WHEN** a caller runs `provider-replay status --config <path> --view summary`
- **THEN** `summary_view.capabilities` MUST include `endpoint_family_counts`
- **AND** the counts MUST be derived from detailed `capabilities.endpoints`
- **AND** the counts MUST include replay `core` and `watch` families when matching endpoints exist
- **AND** `summary_view.capabilities` MUST NOT include the full `endpoints` list
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, or probe unless explicit probe flags are provided
