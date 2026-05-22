## ADDED Requirements

### Requirement: Provider replay mode SHALL serve sector-list through default fixture-backed execution
Replay mode SHALL serve `meta.sector_list` through deterministic fixture-backed execution while preserving live behavior in live mode.

#### Scenario: Replay mode resolves default sector-list fixture
- **WHEN** a caller invokes `meta.sector_list` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `meta-sector-list-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime sector-list code
