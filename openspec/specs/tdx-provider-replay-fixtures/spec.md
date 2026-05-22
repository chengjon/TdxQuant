# tdx-provider-replay-fixtures Specification

## Purpose
TBD - created by archiving change add-provider-replay-fixtures. Update Purpose after archive.
## Requirements
### Requirement: Provider replay fixtures SHALL provide a stable built-in fixture bundle
The system SHALL provide a stable built-in replay fixture bundle for the current high-value provider-facing contracts so callers can validate integrations without live Windows runtime access.

#### Scenario: Consumer enumerates bundled replay fixtures
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the system MUST expose stable fixture names, capability identifiers, file formats, and descriptions for the bundled samples
- **AND** the fixture catalog MUST include representative `block sync` outcomes for at least applied, noop, rejected, and dry-run plan paths
- **AND** bundled block sync fixture names SHOULD follow a stable `block-sync-<mode>-<outcome>.json` naming pattern

### Requirement: Provider replay fixtures SHALL support both JSON and JSONL contracts
The system SHALL support bundled replay samples for synchronous provider JSON responses and asynchronous provider event-row JSONL streams.

#### Scenario: Consumer loads a JSON replay fixture
- **WHEN** a caller loads a bundled synchronous provider fixture
- **THEN** the system MUST return a parsed JSON object that matches the packaged sample
- **AND** block sync fixtures MUST preserve the stabilized `sync` summary fields together with any exposed `block_mutation` governance metadata and audit-artifact descriptors

#### Scenario: Consumer loads a JSONL replay fixture
- **WHEN** a caller loads a bundled provider event fixture
- **THEN** the system MUST return parsed rows in source order without requiring the caller to split lines manually

### Requirement: Provider replay fixtures SHALL remain independent from live runtime execution
The system SHALL keep the replay fixture bundle usable without TongDaXin runtime initialization, live probes, or live Windows-only dependencies.

#### Scenario: Consumer uses fixture loader without live runtime
- **WHEN** a caller loads a replay fixture on a machine without TongDaXin runtime access
- **THEN** the loader MUST still work because it depends only on packaged local assets

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

### Requirement: Provider replay fixtures SHALL include representative subscription-watch resilience artifacts
The system SHALL provide representative replay fixtures for subscription-watch reconnect and degraded runtime-state artifacts in addition to the existing completed-run samples.

#### Scenario: Fixture catalog includes reconnecting and degraded status samples
- **WHEN** a caller enumerates the built-in replay fixture catalog
- **THEN** the catalog MUST include representative `subscription-watch` status fixtures for `reconnecting` and `degraded`

#### Scenario: Fixture catalog includes a completed summary with reconnect history
- **WHEN** a caller enumerates the built-in replay fixture catalog
- **THEN** the catalog MUST include a representative completed `subscription-watch` summary that preserves reconnect history fields

#### Scenario: Existing completed fixtures remain valid with additive resilience fields
- **WHEN** a caller loads the existing completed `subscription-watch` status or summary fixture
- **THEN** the fixture MUST remain valid for the pre-existing completed-run contract
- **AND** any resilience fields added by this change MUST be additive compatibility extensions rather than a breaking schema rewrite

### Requirement: Provider replay fixtures SHALL include representative subscription event-stream transport samples
The system SHALL provide representative replay fixtures for the subscription event-stream transport so callers can validate stream parsing without live Windows runtime access.

#### Scenario: Fixture catalog includes subscription stream frame samples
- **WHEN** a caller enumerates the built-in provider replay fixture catalog
- **THEN** the catalog MUST include representative subscription event-stream samples
- **AND** the samples MUST cover quote, status, heartbeat, reconnecting, degraded, and terminal frame projections

#### Scenario: Stream fixture preserves canonical event rows inside frame payloads
- **WHEN** a caller loads a subscription event-stream replay fixture
- **THEN** quote frames MUST preserve the normalized subscription event row under the frame payload's `event` field
- **AND** transport fields MUST remain outside the normalized event row

#### Scenario: Stream fixture can be loaded without live runtime
- **WHEN** a caller loads subscription event-stream replay fixtures on a machine without TongDaXin runtime access
- **THEN** the loader MUST parse the samples from packaged local assets without live probes or Windows-only dependencies

### Requirement: Provider replay fixtures SHALL include delayed transport playback samples
The system SHALL provide representative replay fixtures that describe delayed playback behavior for provider transport streams.

#### Scenario: Fixture catalog includes delayed playback sample
- **WHEN** a caller enumerates the built-in provider replay fixture catalog
- **THEN** the catalog MUST include a delayed playback transport sample
- **AND** the sample MUST be loadable without live runtime dependencies

#### Scenario: Delayed playback sample preserves canonical event-stream frame shape
- **WHEN** a caller loads the delayed playback transport sample
- **THEN** the sample MUST contain replay frame objects with JSON-compatible status, quote, heartbeat, or terminal frame payloads
- **AND** quote frames MUST include deterministic playback offset metadata

### Requirement: Provider replay fixture descriptors SHALL mark transport replay samples
The system SHALL distinguish transport replay fixtures from synchronous result fixtures and artifact replay fixtures.

#### Scenario: Transport replay descriptors include transport metadata
- **WHEN** a caller enumerates provider replay fixtures
- **THEN** transport replay fixtures MUST include descriptor metadata identifying their transport surface and playback mode

### Requirement: Provider replay fixtures SHALL include a stock-info query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.stock_info` sample for offline stock metadata query validation.

#### Scenario: Consumer enumerates the stock-info fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-stock-info-success`
- **AND** that descriptor MUST identify capability `market.stock_info`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the stock-info fixture
- **WHEN** a caller loads `market-stock-info-success`
- **THEN** the fixture MUST contain capability `market.stock_info`
- **AND** the fixture data MUST preserve representative stock-info rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`

### Requirement: Provider replay fixtures SHALL include a more-info query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.more_info` sample for offline extended stock metadata validation.

#### Scenario: Consumer enumerates the more-info fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-more-info-success`
- **AND** that descriptor MUST identify capability `market.more_info`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the more-info fixture
- **WHEN** a caller loads `market-more-info-success`
- **THEN** the fixture MUST contain capability `market.more_info`
- **AND** the fixture data MUST preserve representative extended stock metadata rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`

### Requirement: Provider replay fixtures SHALL include a cb-info query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.cb_info` sample for offline convertible-bond metadata validation.

#### Scenario: Consumer enumerates the cb-info fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-cb-info-success`
- **AND** that descriptor MUST identify capability `market.cb_info`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the cb-info fixture
- **WHEN** a caller loads `market-cb-info-success`
- **THEN** the fixture MUST contain capability `market.cb_info`
- **AND** the fixture data MUST preserve representative convertible-bond metadata rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`

### Requirement: Provider replay fixtures SHALL include a gb-info query sample
The provider replay fixture bundle SHALL include a representative synchronous `meta.gb_info` sample for offline bonus-share/dividend metadata validation.

#### Scenario: Consumer enumerates the gb-info fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `meta-gb-info-success`
- **AND** that descriptor MUST identify capability `meta.gb_info`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the gb-info fixture
- **WHEN** a caller loads `meta-gb-info-success`
- **THEN** the fixture MUST contain capability `meta.gb_info`
- **AND** the fixture data MUST preserve representative bonus-share/dividend metadata rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`

### Requirement: Provider replay fixtures SHALL include an ipo-info query sample
The provider replay fixture bundle SHALL include a representative synchronous `meta.ipo_info` sample for offline IPO metadata validation.

#### Scenario: Consumer enumerates the ipo-info fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `meta-ipo-info-success`
- **AND** that descriptor MUST identify capability `meta.ipo_info`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the ipo-info fixture
- **WHEN** a caller loads `meta-ipo-info-success`
- **THEN** the fixture MUST contain capability `meta.ipo_info`
- **AND** the fixture data MUST preserve representative IPO metadata rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`

### Requirement: Provider replay fixtures SHALL include a gp-one query sample
The provider replay fixture bundle SHALL include a representative synchronous `meta.gp_one_data` sample for offline per-security metadata validation.

#### Scenario: Consumer enumerates the gp-one fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `meta-gp-one-success`
- **AND** that descriptor MUST identify capability `meta.gp_one_data`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the gp-one fixture
- **WHEN** a caller loads `meta-gp-one-success`
- **THEN** the fixture MUST contain capability `meta.gp_one_data`
- **AND** the fixture data MUST preserve representative per-security metadata rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`

### Requirement: Provider replay fixtures SHALL include a divid-factors query sample
The provider replay fixture bundle SHALL include a representative synchronous `meta.divid_factors` sample for offline dividend-factor metadata validation.

#### Scenario: Consumer enumerates the divid-factors fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `meta-divid-factors-success`
- **AND** that descriptor MUST identify capability `meta.divid_factors`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the divid-factors fixture
- **WHEN** a caller loads `meta-divid-factors-success`
- **THEN** the fixture MUST contain capability `meta.divid_factors`
- **AND** the fixture data MUST preserve representative dividend-factor rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`

### Requirement: Provider replay fixtures SHALL include a stock transaction by-date query sample
The provider replay fixture bundle SHALL include a representative synchronous `transaction.stock_transaction_data_by_date` sample for offline by-date stock transaction query validation.

#### Scenario: Consumer enumerates the stock transaction by-date fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `transaction-stock-transaction-data-by-date-success`
- **AND** that descriptor MUST identify capability `transaction.stock_transaction_data_by_date`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the stock transaction by-date fixture
- **WHEN** a caller loads `transaction-stock-transaction-data-by-date-success`
- **THEN** the fixture MUST contain capability `transaction.stock_transaction_data_by_date`
- **AND** the fixture data MUST preserve representative stock transaction by-date rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve the requested symbols, requested fields, and date selector

### Requirement: Provider replay fixtures SHALL include a market transaction by-date query sample
The provider replay fixture bundle SHALL include a representative synchronous `transaction.market_transaction_data_by_date` sample for offline by-date market transaction query validation.

#### Scenario: Consumer enumerates the market transaction by-date fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `transaction-market-transaction-data-by-date-success`
- **AND** that descriptor MUST identify capability `transaction.market_transaction_data_by_date`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the market transaction by-date fixture
- **WHEN** a caller loads `transaction-market-transaction-data-by-date-success`
- **THEN** the fixture MUST contain capability `transaction.market_transaction_data_by_date`
- **AND** the fixture data MUST preserve representative market transaction by-date rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve the requested fields and date selector

### Requirement: Provider replay fixtures SHALL include a sector transaction by-date query sample
The provider replay fixture bundle SHALL include a representative synchronous `transaction.sector_transaction_data_by_date` sample for offline by-date sector transaction query validation.

#### Scenario: Consumer enumerates the sector transaction by-date fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `transaction-sector-transaction-data-by-date-success`
- **AND** that descriptor MUST identify capability `transaction.sector_transaction_data_by_date`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the sector transaction by-date fixture
- **WHEN** a caller loads `transaction-sector-transaction-data-by-date-success`
- **THEN** the fixture MUST contain capability `transaction.sector_transaction_data_by_date`
- **AND** the fixture data MUST preserve representative sector transaction by-date rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve requested symbols, requested fields, and date selector

### Requirement: Provider replay fixtures SHALL include a sector transaction range query sample
The provider replay fixture bundle SHALL include a representative synchronous `transaction.sector_transaction_data` sample for offline sector transaction range query validation.

#### Scenario: Consumer enumerates the sector transaction range fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `transaction-sector-transaction-data-success`
- **AND** that descriptor MUST identify capability `transaction.sector_transaction_data`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the sector transaction range fixture
- **WHEN** a caller loads `transaction-sector-transaction-data-success`
- **THEN** the fixture MUST contain capability `transaction.sector_transaction_data`
- **AND** the fixture data MUST preserve representative sector transaction range rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve requested symbols, requested fields, and date range

### Requirement: Provider replay fixtures SHALL include a sector-list query sample
The provider replay fixture bundle SHALL include a representative synchronous `meta.sector_list` sample for offline sector-list query validation.

#### Scenario: Consumer enumerates the sector-list fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `meta-sector-list-success`
- **AND** that descriptor MUST identify capability `meta.sector_list`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the sector-list fixture
- **WHEN** a caller loads `meta-sector-list-success`
- **THEN** the fixture MUST contain capability `meta.sector_list`
- **AND** the fixture data MUST preserve representative sector-list rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve the `list_type` query parameter

### Requirement: Provider replay fixtures SHALL include a market-snapshot query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.market_snapshot` sample for offline market-snapshot query validation.

#### Scenario: Consumer enumerates the market-snapshot fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-market-snapshot-success`
- **AND** that descriptor MUST identify capability `market.market_snapshot`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the market-snapshot fixture
- **WHEN** a caller loads `market-market-snapshot-success`
- **THEN** the fixture MUST contain capability `market.market_snapshot`
- **AND** the fixture data MUST preserve representative market-snapshot rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve the requested symbol and requested fields

### Requirement: Provider replay fixtures SHALL include a full-tick query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.full_tick` sample for offline full-tick query validation.

#### Scenario: Consumer enumerates the full-tick fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-full-tick-success`
- **AND** that descriptor MUST identify capability `market.full_tick`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the full-tick fixture
- **WHEN** a caller loads `market-full-tick-success`
- **THEN** the fixture MUST contain capability `market.full_tick`
- **AND** the fixture data MUST preserve representative full-tick rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve the requested symbol and requested fields

