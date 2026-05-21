## ADDED Requirements

### Requirement: Query API management SHALL route market transaction by-date through replay dispatch
The manager market transaction by-date query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager market transaction by-date uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").transaction.market_transaction_data_by_date(...)`
- **THEN** the manager MUST return the `transaction.market_transaction_data_by_date` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for market transaction by-date
- **AND** the manager MUST NOT call the live transaction market transaction by-date bridge implementation
