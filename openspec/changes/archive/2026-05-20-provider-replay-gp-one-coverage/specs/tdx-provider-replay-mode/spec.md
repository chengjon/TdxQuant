# tdx-provider-replay-mode Delta

## ADDED Requirements

### Requirement: Provider replay mode SHALL serve gp-one through default fixture-backed execution
Replay mode SHALL treat `meta.gp_one_data` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default gp-one fixture
- **WHEN** a caller invokes `meta.gp_one_data` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `meta-gp-one-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime gp-one code

