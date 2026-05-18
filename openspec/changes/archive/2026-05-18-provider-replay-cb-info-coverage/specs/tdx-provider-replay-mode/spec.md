# tdx-provider-replay-mode Delta

## ADDED Requirements

### Requirement: Provider replay mode SHALL serve cb-info through default fixture-backed execution
Replay mode SHALL treat `market.cb_info` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default cb-info fixture
- **WHEN** a caller invokes `market.cb_info` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `market-cb-info-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime cb-info code
