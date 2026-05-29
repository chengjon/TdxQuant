## ADDED Requirements

### Requirement: Worker bridge SHALL expose restart preflight view

The worker bridge HTTP control plane SHALL expose a read-only subscription-watch restart preflight endpoint without changing default status, summary, diagnostics, event, stream, start, stop, or restart behavior.

#### Scenario: Caller requests watch restart preflight

- **WHEN** a caller invokes `GET /bridge/v1/watch/restart-preflight`
- **THEN** the bridge MUST dispatch to the background controller restart preflight operation
- **AND** the response MUST preserve the controller preflight envelope
- **AND** the bridge MUST NOT stop, start, restart, schedule automatic backoff, run a supervisor loop, infer ownership from port state, or change SSE/event-stream behavior.
