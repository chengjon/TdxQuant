## ADDED Requirements

### Requirement: Report preset registry SHALL expose Ping An sell submit-once audit views

The runtime report preset registry SHALL expose Ping An `sell_submit_once` trade-audit views for exception and status diagnostics.

#### Scenario: Caller discovers Ping An sell submit-once daily audit presets

- **WHEN** a caller loads runtime report presets
- **THEN** the registry MUST include daily Ping An `sell_submit_once` exception, rejected, and failed presets
- **AND** each preset MUST filter `broker=pingan` and `method=sell_submit_once`

#### Scenario: Caller discovers Ping An sell submit-once period audit presets

- **WHEN** a caller loads runtime report presets
- **THEN** the registry MUST include period Ping An `sell_submit_once` exception, rejected, and failed presets
- **AND** each preset MUST filter `broker=pingan` and `method=sell_submit_once`
