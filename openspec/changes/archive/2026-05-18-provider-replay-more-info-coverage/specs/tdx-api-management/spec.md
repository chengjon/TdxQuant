# tdx-api-management Delta

## ADDED Requirements

### Requirement: Query API management SHALL route more-info through replay dispatch
The manager more-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager more-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").market.more_info(...)`
- **THEN** the manager MUST return the `market.more_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for more-info
- **AND** the manager MUST NOT call the live market more-info bridge implementation
