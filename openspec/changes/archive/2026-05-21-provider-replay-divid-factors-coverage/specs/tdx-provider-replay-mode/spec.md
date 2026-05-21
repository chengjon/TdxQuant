# tdx-provider-replay-mode Delta

## ADDED Requirements

### Requirement: Provider replay mode SHALL serve divid-factors through default fixture-backed execution
Replay mode SHALL treat `meta.divid_factors` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default divid-factors fixture
- **WHEN** a caller invokes `meta.divid_factors` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `meta-divid-factors-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime divid-factors code

