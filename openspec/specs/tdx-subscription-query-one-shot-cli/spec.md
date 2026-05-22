# tdx-subscription-query-one-shot-cli Specification

## Purpose
TBD - created by archiving change subscription-query-one-shot-cli. Update Purpose after archive.
## Requirements
### Requirement: Subscription one-shot API SHALL invoke runtime subscription methods exactly once
The system SHALL provide query-style one-shot operations for `subscribe_hq`, `unsubscribe_hq`, and `get_subscribe_hq_stock_list` by opening a runtime subscription session, invoking the requested method once, and closing the session.

#### Scenario: Caller invokes one-shot subscribe
- **WHEN** a caller requests one-shot subscription subscribe with one or more stock codes
- **THEN** the system MUST call the runtime `subscribe_hq` method once
- **AND** the result MUST include one-shot operation metadata
- **AND** the operation MUST NOT start a `subscription-watch` run or worker bridge controller

#### Scenario: Caller invokes one-shot unsubscribe
- **WHEN** a caller requests one-shot subscription unsubscribe with one or more stock codes
- **THEN** the system MUST call the runtime `unsubscribe_hq` method once
- **AND** the result MUST include one-shot operation metadata

#### Scenario: Caller lists subscribed stocks
- **WHEN** a caller requests the one-shot subscribed stock list
- **THEN** the system MUST call the runtime `get_subscribe_hq_stock_list` method once
- **AND** the result MUST include one-shot operation metadata

### Requirement: Subscription one-shot API SHALL not claim long-running watch governance
The system SHALL distinguish one-shot subscription operations from `subscription-watch` foreground runs, background worker control, provider SSE streams, and reconnect/backoff governance.

#### Scenario: Caller receives one-shot boundary metadata
- **WHEN** a caller invokes any one-shot subscription operation
- **THEN** the result MUST identify `mode` as `one_shot`
- **AND** the result MUST state that no foreground watch run, background worker, or event-stream transport was started

### Requirement: Subscription one-shot replay SHALL be explicitly unsupported
The system SHALL reject replay mode for one-shot subscription CLI operations until dedicated one-shot subscription replay fixtures exist.

#### Scenario: Caller requests replay mode for one-shot subscription operation
- **WHEN** a caller executes a one-shot subscription CLI command with `provider_mode=replay`
- **THEN** the command MUST return an invalid request result
- **AND** the result MUST identify the replay capability that is not currently supported

### Requirement: Subscription one-shot replay SHALL preserve one-shot boundaries
Subscription one-shot replay SHALL exercise only the one-shot subscribe, unsubscribe, and list contracts and SHALL NOT claim long-running subscription governance.

#### Scenario: Replay one-shot response identifies one-shot scope
- **WHEN** a caller receives a replay response for one-shot subscription subscribe, unsubscribe, or list
- **THEN** the response MUST include metadata identifying `scope` as `one_shot`
- **AND** the response MUST NOT include foreground watch run, background worker, or SSE stream lifecycle metadata

