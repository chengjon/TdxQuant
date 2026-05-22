## ADDED Requirements

### Requirement: Desktop broker capability probe SHALL be available through a preset-backed trade run path
The PingAn desktop extended broker capability probe SHALL be invocable through a stable trade preset without requiring buy or submit order fields and without changing the probe's diagnostic-only behavior.

#### Scenario: Caller runs the broker capability preset
- **WHEN** a caller executes `trade run --preset broker-capabilities-default`
- **THEN** the trade runner dispatches to the existing `broker-capabilities` probe
- **AND** the caller is not required to provide order fields such as `port`, `code`, `price`, or `quantity`
- **AND** the result remains the existing diagnostic capability payload

#### Scenario: Broker capability preset remains non-mutating
- **WHEN** the broker capability preset is resolved
- **THEN** it does not execute funds extraction, positions extraction, cancel requests, or broker-native push subscriptions
- **AND** it does not become part of the default buy or submit trade flow
