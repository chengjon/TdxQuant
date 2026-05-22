## ADDED Requirements

### Requirement: Trade audit cross-ledger query SHALL return read-only count aggregation

The cross-ledger query SHALL include deterministic count aggregation for the filtered trade audit set without mutating source audit files or ledgers.

#### Scenario: Query aggregates filtered audit entries

- **WHEN** a caller queries trade audit entries with or without filters
- **THEN** the result MUST include counts grouped by status, method, and broker
- **AND** the result MUST include combined broker/method/status count rows

#### Scenario: Query aggregation is independent of row limit

- **WHEN** a caller supplies a row limit
- **THEN** returned rows MAY be limited
- **AND** aggregation MUST still summarize the full filtered audit set before the limit

#### Scenario: Query aggregation preserves malformed dimension visibility

- **WHEN** an indexed audit entry is missing broker, method, or status
- **THEN** aggregation MUST count the missing dimension as `unknown`
- **AND** the query MUST NOT drop the entry only because an aggregation dimension is missing

