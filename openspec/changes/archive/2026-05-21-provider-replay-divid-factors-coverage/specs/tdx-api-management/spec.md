# tdx-api-management Delta

## ADDED Requirements

### Requirement: Query API management SHALL route divid-factors through replay dispatch
The manager divid-factors query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager divid-factors uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.divid_factors(...)`
- **THEN** the manager MUST return the `meta.divid_factors` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for divid-factors
- **AND** the manager MUST NOT call the live meta divid-factors bridge implementation

