# tdx-provider-replay-fixtures Delta

## ADDED Requirements

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

