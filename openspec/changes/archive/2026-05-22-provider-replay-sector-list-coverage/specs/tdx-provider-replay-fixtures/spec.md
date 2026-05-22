## ADDED Requirements

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
