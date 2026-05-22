## ADDED Requirements

### Requirement: Query API management SHALL route sector-list through replay dispatch
The manager sector-list query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager sector-list uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.sector_list(...)`
- **THEN** the manager MUST return the `meta.sector_list` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for sector-list
- **AND** the manager MUST NOT call the live meta sector-list bridge implementation
