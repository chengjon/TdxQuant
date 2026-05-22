## ADDED Requirements

### Requirement: Query API management SHALL route market-snapshot through replay dispatch
The manager market-snapshot query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager market-snapshot uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").market.market_snapshot(...)`
- **THEN** the manager MUST return the `market.market_snapshot` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for market-snapshot
- **AND** the manager MUST NOT call the live market-snapshot bridge implementation
