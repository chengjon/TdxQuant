## ADDED Requirements

### Requirement: Query API management SHALL route full-tick through replay dispatch
The manager full-tick query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager full-tick uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").market.full_tick(...)`
- **THEN** the manager MUST return the `market.full_tick` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for full-tick
- **AND** the manager MUST NOT call the live full-tick bridge implementation
