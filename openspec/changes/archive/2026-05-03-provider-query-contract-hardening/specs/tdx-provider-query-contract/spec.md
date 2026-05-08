## ADDED Requirements

### Requirement: Query providers SHALL return stable query metadata for market, meta, financial, and transaction capabilities
The system SHALL attach stable query metadata to provider-facing results for `market`, `meta`, `financial`, and `transaction` capabilities so callers can consume these queries through a common adapter without losing capability-specific payload rows.

#### Scenario: Market query returns single-symbol query metadata
- **WHEN** a caller executes a market query such as snapshot or full-tick for one security
- **THEN** the result MUST include `data.query_meta.query_kind`, `data.query_meta.row_count`, `data.query_meta.requested_fields`, and `data.query_meta.returned_fields`
- **AND** the result MUST include the resolved `symbol` under `data.query_meta` when the query is semantically a single-symbol query

#### Scenario: Financial time-range query returns date-range query metadata
- **WHEN** a caller executes a professional financial query over a time range
- **THEN** the result MUST include `data.query_meta.query_kind`, `data.query_meta.row_count`, `data.query_meta.requested_fields`, and `data.query_meta.returned_fields`
- **AND** the result MUST include `data.query_meta.date_range` metadata that reflects the requested time window

#### Scenario: Meta list-style query returns list-oriented metadata
- **WHEN** a caller executes a metadata list query such as stock-list or sector-list
- **THEN** the result MUST include `data.query_meta.query_kind`, `data.query_meta.row_count`, `data.query_meta.requested_fields`, and `data.query_meta.returned_fields`
- **AND** the result MAY omit symbol-specific fields when the query is not tied to a single security

#### Scenario: Meta query preserves residual selectors in query_params
- **WHEN** a covered meta query uses selectors such as `list_type`, `block_type`, `ipo_type`, or `count` that do not map cleanly to shared top-level selector fields
- **THEN** those selectors MUST be preserved in `data.query_meta.query_params`
- **AND** the result MUST still use shared fields such as `market`, `block_code`, `symbol`, or `date_range` when those common projections are semantically available

#### Scenario: Market kline query reports multi-symbol and date-range metadata
- **WHEN** a caller executes `market.kline`
- **THEN** the result MUST expose `data.query_meta.query_kind = "market.kline"`
- **AND** the result MUST use `data.query_meta.symbols` and `data.query_meta.date_range`
- **AND** kline-specific selectors such as `period`, `count`, `dividend_type`, or `fill_data` MUST remain machine-readable via `data.query_meta.query_params`

### Requirement: Query providers SHALL preserve domain-native rows while normalizing summary fields
The system SHALL keep capability-specific result rows in their native shape while normalizing only the common query summary fields.

#### Scenario: Transaction market query preserves native row structure
- **WHEN** a caller executes a transaction market query
- **THEN** the result MUST keep transaction rows in their native transaction schema
- **AND** the result MUST expose normalized query summary fields under `data.query_meta` separately from the row payloads

#### Scenario: Empty query result still returns stable metadata
- **WHEN** a query completes successfully with no matching rows
- **THEN** the result MUST still include `data.query_meta.query_kind`, `data.query_meta.row_count`, `data.query_meta.requested_fields`, and `data.query_meta.returned_fields`
- **AND** `data.query_meta.row_count` MUST be `0`
- **AND** `data.query_meta.returned_fields` MUST be `[]`

#### Scenario: Query metadata separates effective requested fields from actual returned fields
- **WHEN** a covered query supports field selection
- **THEN** `data.query_meta.requested_fields` MUST reflect the normalized effective field list sent to the provider
- **AND** `data.query_meta.returned_fields` MUST reflect the actual row/header fields returned by the provider rather than the caller's raw input text

### Requirement: Query providers SHALL use stable query-kind literals and selector semantics
The system SHALL use stable `query_kind` literals and SHALL keep selector fields machine-readable instead of relying on free-form descriptive text.

#### Scenario: Query result uses stable query-kind literal
- **WHEN** any covered query capability returns successfully
- **THEN** `data.query_meta.query_kind` MUST use a provider-owned stable literal rather than a free-form description string
- **AND** the stable literal MUST match the capability-style `{domain}.{method}` registry for the covered method

#### Scenario: Query result does not mix single and plural selector fields
- **WHEN** a query result includes symbol selectors or date selectors
- **THEN** it MUST NOT expose both `symbol` and `symbols` for the same query
- **AND** it MUST NOT expose both `date` and `date_range` for the same query

#### Scenario: Single-value and list-value selector mapping stay distinct
- **WHEN** a covered query is driven by a single security code parameter
- **THEN** the result MUST use `data.query_meta.symbol`
- **AND** it MUST NOT collapse that selector into `symbols`
- **WHEN** a covered query is driven by a list of security codes
- **THEN** the result MUST use `data.query_meta.symbols`
