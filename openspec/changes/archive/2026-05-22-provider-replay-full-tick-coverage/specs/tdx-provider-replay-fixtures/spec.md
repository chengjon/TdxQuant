## ADDED Requirements

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
