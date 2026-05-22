## ADDED Requirements

### Requirement: Provider replay mode SHALL serve one-shot subscription operations through default fixtures
Replay mode SHALL serve one-shot subscription subscribe, unsubscribe, and list operations through deterministic fixture-backed execution while preserving live behavior in live mode.

#### Scenario: Replay mode resolves default one-shot subscription fixtures
- **WHEN** a caller invokes one of `subscription.subscribe_hq`, `subscription.unsubscribe_hq`, or `subscription.get_subscribe_hq_stock_list` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve the matching one-shot subscription fixture
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT open a live runtime subscription session
