## ADDED Requirements

### Requirement: Query API management SHALL route sector transaction range through replay dispatch
The manager sector transaction range query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager sector transaction range uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data(...)`
- **THEN** the manager MUST return the `transaction.sector_transaction_data` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for sector transaction range
- **AND** the manager MUST NOT call the live transaction sector transaction range bridge implementation
