# tdx-provider-replay-fixtures Delta

## ADDED Requirements

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

