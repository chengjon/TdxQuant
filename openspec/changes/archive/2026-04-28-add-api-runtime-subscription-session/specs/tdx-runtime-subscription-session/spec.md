## ADDED Requirements

### Requirement: Runtime subscription session SHALL keep TongDaXin runtime initialized across multiple subscription operations
The system SHALL provide a persistent TongDaXin runtime subscription session that initializes `tqcenter` once and keeps that runtime available until the caller explicitly closes the session.

#### Scenario: Caller reuses one session across multiple subscription operations
- **WHEN** a caller opens a runtime subscription session and invokes `subscribe_hq(...)` followed by `get_subscribe_hq_stock_list()`
- **THEN** both operations MUST execute against the same initialized TongDaXin runtime session without closing `tqcenter` between calls

### Requirement: Runtime subscription session SHALL expose official subscription governance operations
The system SHALL expose `subscribe_hq`, `unsubscribe_hq`, and `get_subscribe_hq_stock_list` from the persistent session and SHALL preserve the official callback-driven update model for subscription registration.

#### Scenario: Caller subscribes with explicit stock list and callback
- **WHEN** a caller invokes `subscribe_hq(stock_list=[...], callback=...)` on an open runtime subscription session
- **THEN** the session MUST delegate the exact stock list and callback to the TongDaXin runtime without rewriting the callback contract

#### Scenario: Caller lists current subscriptions from the active session
- **WHEN** a caller invokes `get_subscribe_hq_stock_list()` on an open runtime subscription session
- **THEN** the session MUST return the current subscription list for that same session

#### Scenario: Caller unsubscribes from an explicit stock list
- **WHEN** a caller invokes `unsubscribe_hq(stock_list=[...])` on an open runtime subscription session
- **THEN** the session MUST delegate the exact stock list to the TongDaXin runtime without reinitializing the session

### Requirement: Runtime subscription session SHALL close deterministically
The system SHALL let callers close a runtime subscription session explicitly and SHALL reject further subscription operations after close instead of silently reopening a new runtime behind the caller's back.

#### Scenario: Caller closes the session explicitly
- **WHEN** a caller closes a runtime subscription session
- **THEN** the system MUST close the underlying TongDaXin runtime exactly once and mark the session unavailable for further use

#### Scenario: Caller uses a closed session
- **WHEN** a caller invokes `subscribe_hq(...)`, `unsubscribe_hq(...)`, or `get_subscribe_hq_stock_list()` after the session is closed
- **THEN** the session MUST return a structured invalid-request error instead of reopening implicitly
