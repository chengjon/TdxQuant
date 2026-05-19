# tdx-api-management Delta

## ADDED Requirements

### Requirement: Query API management SHALL route ipo-info through replay dispatch
The manager ipo-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager ipo-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.ipo_info(...)`
- **THEN** the manager MUST return the `meta.ipo_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for ipo-info
- **AND** the manager MUST NOT call the live meta ipo-info bridge implementation

