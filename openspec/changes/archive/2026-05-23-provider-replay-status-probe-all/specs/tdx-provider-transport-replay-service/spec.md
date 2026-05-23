## ADDED Requirements

### Requirement: Provider replay status SHALL support an all-surfaces probe shortcut
The provider replay status CLI SHALL expose a `--probe-all` shortcut that enables all existing read-only status probes without changing lifecycle management behavior.

#### Scenario: Caller probes all provider replay surfaces
- **WHEN** a caller runs `provider-replay status --probe-all`
- **THEN** the status command MUST request health, watch-status, watch-events, and watch-stream probes
- **AND** each probe MUST use the configured token and probe timeout
- **AND** lifecycle `start_stop_managed=false` and `daemon_managed=false` MUST remain unchanged

#### Scenario: Caller uses individual probe flags
- **WHEN** a caller runs `provider-replay status` with any existing individual probe flag
- **THEN** that individual probe behavior MUST remain available
- **AND** `--probe-all` MUST NOT be required for narrow checks
