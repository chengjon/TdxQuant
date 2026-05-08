## ADDED Requirements

### Requirement: Provider replay fixtures SHALL cover representative query contracts for market, meta, financial, and transaction
The system SHALL provide representative replay fixtures for the covered query domains so callers can validate hardened query contracts without live runtime access.

#### Scenario: Query fixture catalog includes representative covered query fixtures
- **WHEN** a caller enumerates the built-in replay fixture catalog
- **THEN** the catalog MUST include representative fixtures for `market`, `meta`, `financial`, and `transaction` query capabilities
- **AND** those representatives MUST cover at least success, empty-result, and failure outcomes across the covered query domains
- **AND** the minimum representative set MUST include `market.snapshot`, `market.kline`, `meta.stock_list`, `meta.sector_stocks`, `financial.financial_data`, `financial.financial_data_by_date`, `transaction.stock_transaction_data`, and `transaction.market_transaction_data`

#### Scenario: Query replay fixture preserves hardened query metadata
- **WHEN** a caller loads a covered query replay fixture
- **THEN** the fixture payload MUST preserve the hardened query metadata required by the provider query contract
- **AND** the fixture MUST preserve any domain-native `rows` shape for that capability
- **AND** the hardened metadata MUST live under `data.query_meta`
