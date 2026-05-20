# tdx-api-management Delta

## ADDED Requirements

### Requirement: Query API management SHALL route gp-one through replay dispatch
The manager gp-one query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager gp-one uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.gp_one_data(...)`
- **THEN** the manager MUST return the `meta.gp_one_data` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for gp-one
- **AND** the manager MUST NOT call the live meta gp-one bridge implementation

