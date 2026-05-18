# tdx-api-management Delta

## ADDED Requirements

### Requirement: Query API management SHALL route cb-info through replay dispatch
The manager cb-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager cb-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").market.cb_info(...)`
- **THEN** the manager MUST return the `market.cb_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for cb-info
- **AND** the manager MUST NOT call the live market cb-info bridge implementation
