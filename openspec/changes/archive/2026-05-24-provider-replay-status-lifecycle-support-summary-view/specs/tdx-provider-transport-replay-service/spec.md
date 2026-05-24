## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose lifecycle support boundary

The provider replay status summary view SHALL expose compact lifecycle support metadata derived from the detailed lifecycle payload without adding start, stop, restart, scheduler, daemon, supervisor, live-session, or write behavior.

#### Scenario: Caller requests provider replay status lifecycle support summary

- **WHEN** a caller executes `provider-replay status --config <path> --view summary`
- **THEN** the summary view MUST include `lifecycle.control_supported`
- **AND** the summary view MUST include `lifecycle.managed_operation_count`
- **AND** `lifecycle.control_supported` MUST be `false` for the current replay provider
- **AND** `lifecycle.managed_operation_count` MUST be `0` for the current replay provider
- **AND** the command MUST NOT start, stop, restart, schedule, daemonize, supervise, or observe a live market session

