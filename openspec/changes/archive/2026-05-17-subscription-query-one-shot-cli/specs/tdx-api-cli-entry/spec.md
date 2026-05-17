## ADDED Requirements

### Requirement: API CLI SHALL expose subscription one-shot commands
The system SHALL expose query-style one-shot subscription commands under the nested `api` CLI namespace.

#### Scenario: Caller subscribes through API CLI
- **WHEN** a caller executes `api subscription-subscribe --code <stock>`
- **THEN** the CLI MUST dispatch the one-shot runtime subscription subscribe operation

#### Scenario: Caller unsubscribes through API CLI
- **WHEN** a caller executes `api subscription-unsubscribe --code <stock>`
- **THEN** the CLI MUST dispatch the one-shot runtime subscription unsubscribe operation

#### Scenario: Caller lists runtime subscribed stocks through API CLI
- **WHEN** a caller executes `api subscription-list`
- **THEN** the CLI MUST dispatch the one-shot runtime subscribed-stock-list operation
