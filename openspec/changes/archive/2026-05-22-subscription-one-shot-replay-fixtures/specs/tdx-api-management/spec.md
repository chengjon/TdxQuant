## ADDED Requirements

### Requirement: Query API management SHALL expose one-shot subscription manager methods
The API manager SHALL expose one-shot subscription subscribe, unsubscribe, and list methods that preserve live behavior in live mode and use fixture-backed execution in replay mode.

#### Scenario: Manager one-shot subscription uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").runtime.subscription_subscribe(...)`, `subscription_unsubscribe(...)`, or `subscription_list()`
- **THEN** the manager MUST return the corresponding replay fixture result
- **AND** the manager MUST NOT open a live runtime subscription session

#### Scenario: Manager one-shot subscription delegates to live wrapper in live mode
- **WHEN** a caller invokes the manager one-shot subscription methods in live mode
- **THEN** the manager MUST delegate to the existing `RuntimeApi.subscription_*` one-shot wrappers
- **AND** the manager MUST preserve manager metadata in the result
