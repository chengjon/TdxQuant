## ADDED Requirements

### Requirement: Provider capability discovery SHALL expose query metadata for covered query capabilities
The system SHALL expose stable query-oriented metadata for the covered `market`, `meta`, `financial`, and `transaction` capabilities so upstream callers can reason about their invocation shape before issuing requests.

#### Scenario: Capability discovery reports query shapes and replay support
- **WHEN** a caller requests provider capability discovery
- **THEN** each covered query capability entry MUST expose machine-readable `query_metadata`
- **AND** `query_metadata.query_shapes` MUST be a list of objects
- **AND** each shape object MUST include at least `query_kind` and `selectors`
- **AND** each covered query capability entry MUST indicate replay support within `query_metadata`

#### Scenario: Capability discovery reports field-selection support for covered queries
- **WHEN** a caller requests provider capability discovery
- **THEN** each covered query capability entry MUST indicate within `query_metadata` whether the capability supports explicit requested-field selection
- **AND** the entry MUST indicate that empty successful result sets are valid outcomes for query consumption

#### Scenario: Capability discovery shape captures residual selector knobs
- **WHEN** a covered query capability needs selector parameters that are not represented by shared query fields such as `symbol`, `symbols`, `date`, `date_range`, `market`, or `block_code`
- **THEN** the corresponding `query_metadata.query_shapes` entry MUST expose those residual knobs via a machine-readable `query_params` field name list
