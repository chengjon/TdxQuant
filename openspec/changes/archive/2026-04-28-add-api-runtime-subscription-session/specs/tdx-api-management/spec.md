## ADDED Requirements

### Requirement: Query API management SHALL expose persistent runtime subscription sessions through the runtime domain
The system SHALL expose a persistent TongDaXin runtime subscription-session factory through `manager.runtime` instead of presenting official subscription governance as one-shot manager calls.

#### Scenario: Caller opens a runtime subscription session from the manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to open a persistent subscription session through `manager.runtime.open_subscription_session(...)`

### Requirement: Query API management SHALL keep runtime subscription session operations inside the manager envelope
The system SHALL keep manager-owned runtime subscription operations inside the existing manager metadata and timing model while requiring callers to provide explicit subscription inputs.

#### Scenario: Caller subscribes through a manager-owned runtime session
- **WHEN** a caller invokes `subscribe_hq(...)` on a session created by `manager.runtime.open_subscription_session(...)`
- **THEN** the returned result MUST include `runtime` domain metadata, method timing, and a stable session identifier

#### Scenario: Caller lists or removes subscriptions through the same manager-owned session
- **WHEN** a caller invokes `get_subscribe_hq_stock_list()` or `unsubscribe_hq(...)` on a session created by `manager.runtime.open_subscription_session(...)`
- **THEN** the manager MUST preserve the active strategy path and session identity for those operations without inferring subscription contents from API profile defaults
