# tdx-desktop-trading-extended-broker-capabilities Specification

## Purpose
TBD - created by archiving change desktop-trade-extended-broker-capabilities. Update Purpose after archive.
## Requirements
### Requirement: Desktop trade broker capability probe SHALL expose explicit status evidence and boundaries
The system SHALL provide a PingAn desktop extended broker capability probe whose payload records each capability with explicit `status`, `evidence`, and `boundary` fields.

#### Scenario: Caller probes extended broker capabilities
- **WHEN** a caller requests the PingAn desktop extended broker capability probe
- **THEN** the result MUST include a stable schema version
- **AND** the result MUST include entries for funds, positions, cancel order, and broker-native push
- **AND** each entry MUST include status, evidence, and boundary metadata

### Requirement: Funds and positions probes SHALL remain read-only
The system SHALL represent funds and positions as read-only probe entries and MUST NOT execute live account or holding extraction as part of this probe.

#### Scenario: Caller inspects read-only funds and positions boundaries
- **WHEN** a caller requests the extended broker capability probe
- **THEN** the funds entry MUST identify its side effect as `none`
- **AND** the positions entry MUST identify its side effect as `none`
- **AND** both entries MUST state whether the current gateway capability flag supports the data surface

### Requirement: Cancel order capability SHALL be classified as broker-state mutating
The system SHALL classify cancel order separately from read-only probes and MUST mark its side-effect boundary as broker-state mutating even when no cancel execution is available.

#### Scenario: Caller inspects cancel order boundary
- **WHEN** a caller requests the extended broker capability probe
- **THEN** the cancel-order entry MUST identify its side effect as `broker_state_mutating`
- **AND** the entry MUST state that the probe does not submit a cancel request
- **AND** the entry MUST report support using the current gateway cancel capability flag

### Requirement: Broker-native push capability SHALL expose feasibility boundary
The system SHALL expose broker-native push as a feasibility boundary and MUST NOT report provider subscription/SSE projections as broker-native push support.

#### Scenario: Caller inspects broker-native push boundary
- **WHEN** a caller requests the extended broker capability probe
- **THEN** the broker-native push entry MUST identify whether a broker-native event source is integrated
- **AND** the entry MUST state that existing provider event streams do not satisfy broker-native push support

### Requirement: Extended broker capability risk documentation SHALL be independent
The system SHALL include an independent risk document for extended desktop broker capabilities and SHALL reference it from the probe payload.

#### Scenario: Caller receives risk documentation reference
- **WHEN** a caller requests the extended broker capability probe
- **THEN** the result MUST include a path to the risk document
- **AND** the document MUST describe read-only, local-state-mutating, and broker-state-mutating boundaries

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

