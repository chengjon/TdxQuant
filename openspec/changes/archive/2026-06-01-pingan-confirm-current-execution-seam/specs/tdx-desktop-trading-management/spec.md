## ADDED Requirements

### Requirement: Desktop trading management SHALL route PingAn confirm-current through an internal confirm execution seam
The desktop trading management layer SHALL route `TdxTradeManager.pingan.confirm_current(...)` through an internal confirm-current execution seam while preserving the public manager contract, method identity, lifecycle/broker readiness gates, dialog dispatch behavior, audit metadata, and artifact behavior.

#### Scenario: Confirm-current uses the internal confirm execution seam

- **WHEN** a caller executes `TdxTradeManager.pingan.confirm_current(...)`
- **THEN** the manager MUST route the normalized confirm-current request through the internal confirm execution seam before UI lookup or click dispatch
- **AND** the normalized request MUST preserve `method=confirm_current`, timing label `pingan.confirm_current`, effective profile options, and a null request context
- **AND** the public result MUST preserve existing confirm-current metadata, safety, timing, and artifact behavior

#### Scenario: Confirm-current keeps order and desktop primitive boundaries separate

- **WHEN** the internal confirm execution seam dispatches a confirm-current request
- **THEN** the dispatch MUST continue to use the existing confirm/result dialog lookup and click flow
- **AND** the system MUST NOT force confirm-current into the order-specific `PingAnExecutionRequest`
- **AND** the system MUST NOT introduce a new public command, catalog entry, task preset, workflow builder, or desktop primitive for confirm-current seam routing

