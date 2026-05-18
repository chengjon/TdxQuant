# tdx-provider-replay-mode Delta

## ADDED Requirements

### Requirement: Provider replay mode SHALL serve gb-info through default fixture-backed execution
Replay mode SHALL treat `meta.gb_info` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default gb-info fixture
- **WHEN** a caller invokes `meta.gb_info` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `meta-gb-info-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime gb-info code

