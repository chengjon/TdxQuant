## ADDED Requirements

### Requirement: Provider replay status SHALL optionally probe configured replay service health

The provider replay lifecycle status SHALL support an explicit, read-only health probe for the configured replay HTTP service without taking ownership of daemon lifecycle management.

#### Scenario: Caller builds status without requesting a health probe

- **WHEN** a caller builds provider replay lifecycle status without a probe result
- **THEN** the status MUST remain static and report `runtime.health_probe.status=not_requested`
- **AND** it MUST continue to report `runtime.runtime_observed=false`

#### Scenario: Caller requests a provider replay health probe

- **WHEN** a caller explicitly requests a provider replay health probe for a configured replay service
- **THEN** the probe MUST call the configured `/provider/v1/replay/health` endpoint with the configured bearer token
- **AND** the resulting status MUST report whether the replay service was reachable, the HTTP status if available, and the configured timeout
- **AND** the status MUST NOT expose the bearer token
- **AND** lifecycle fields MUST continue to report no managed start/stop/restart behavior

#### Scenario: Caller requests provider-replay status probe through the CLI

- **WHEN** a caller executes `provider-replay status --config <path> --probe-health`
- **THEN** the CLI MUST include the explicit replay health probe result in the returned lifecycle status
- **AND** the command MUST NOT start, stop, restart, or supervise the replay service
