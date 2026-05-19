# tdx-provider-replay-fixtures Delta

## ADDED Requirements

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

