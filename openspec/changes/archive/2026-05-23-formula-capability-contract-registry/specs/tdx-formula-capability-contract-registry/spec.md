## ADDED Requirements

### Requirement: Formula capability registry SHALL expose per-capability contract status
The system SHALL expose a read-only formula capability registry where each public formula capability declares its contract status, evidence, replay support, provider-contract stability, and boundary.

#### Scenario: Caller inspects formula capability statuses
- **WHEN** a caller requests the formula capability registry
- **THEN** the result MUST include `formula.screen` with provider-contract-stable status, fixture evidence, and replay support
- **AND** the result MUST include legacy formula bridge capabilities with explicit bridge-only status

#### Scenario: Bridge-only formula capabilities are not advertised as provider-stable
- **WHEN** a caller inspects a legacy formula capability such as `formula.xg`, `formula.zb`, or `formula.get_data`
- **THEN** the registry MUST mark `provider_contract_stable` as false
- **AND** the boundary MUST state that the capability is not available as a stable provider/replay contract

### Requirement: Formula registry discovery SHALL be non-executing
The system SHALL expose formula registry discovery without invoking any formula execution, provider bridge, replay fixture, or live TongDaXin integration.

#### Scenario: Manager discovery does not run formulas
- **WHEN** a caller invokes formula capability discovery through `TdxApiManager.formula`
- **THEN** the manager MUST return registry metadata without calling formula execution methods

#### Scenario: CLI discovery prints registry metadata
- **WHEN** a caller invokes the formula capability registry CLI entry
- **THEN** the CLI MUST dispatch through the manager discovery path
- **AND** the response MUST preserve explicit status and boundary fields for every listed capability
