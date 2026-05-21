# tdx-provider-replay-fixtures Delta

## ADDED Requirements

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

