## ADDED Requirements

### Requirement: Worker bridge SHALL expose explicit supervisor tick

The worker bridge HTTP control plane SHALL expose an explicit operator-triggered subscription-watch supervisor tick endpoint without changing default status, summary, diagnostics, event, stream, start, stop, restart, or restart-preflight behavior.

#### Scenario: Caller triggers supervisor tick

- **WHEN** a caller sends `POST /bridge/v1/watch/supervisor-tick`
- **THEN** the bridge MUST dispatch to the background controller supervisor tick operation
- **AND** the response MUST preserve the controller supervisor tick envelope
- **AND** the bridge MUST NOT run a loop, schedule automatic retry, infer ownership from port state, or change SSE/event-stream behavior.

#### Scenario: Registry and CLI dispatch supervisor tick

- **WHEN** a caller invokes the registry helper or `bridge watch-supervisor-tick`
- **THEN** the call MUST use `POST /bridge/v1/watch/supervisor-tick`
- **AND** it MUST NOT call restart, restart-preflight, start, stop, status, events, or logs routes.
