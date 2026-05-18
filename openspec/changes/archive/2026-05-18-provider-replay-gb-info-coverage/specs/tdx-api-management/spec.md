# tdx-api-management Delta

## ADDED Requirements

### Requirement: Query API management SHALL route gb-info through replay dispatch
The manager gb-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager gb-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.gb_info(...)`
- **THEN** the manager MUST return the `meta.gb_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for gb-info
- **AND** the manager MUST NOT call the live meta gb-info bridge implementation

