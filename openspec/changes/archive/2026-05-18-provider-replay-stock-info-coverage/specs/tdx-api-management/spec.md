# tdx-api-management Delta

## ADDED Requirements

### Requirement: Query API management SHALL route stock-info through replay dispatch
The manager stock-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager stock-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").market.stock_info(...)`
- **THEN** the manager MUST return the `market.stock_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for stock-info
- **AND** the manager MUST NOT call the live market stock-info bridge implementation
