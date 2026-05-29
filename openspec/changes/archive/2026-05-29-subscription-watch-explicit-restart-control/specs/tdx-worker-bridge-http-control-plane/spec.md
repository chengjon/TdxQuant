## ADDED Requirements

### Requirement: Worker bridge SHALL expose explicit watch restart

The worker bridge HTTP control plane SHALL expose an explicit operator-triggered subscription-watch restart endpoint without changing default status, summary, diagnostics, event, or stream behavior.

#### Scenario: Caller posts watch restart

- **WHEN** a caller invokes `POST /bridge/v1/watch/restart`
- **THEN** the bridge MUST dispatch to the background controller restart operation
- **AND** it MUST pass optional `reason` and `grace_period_seconds`
- **AND** the response MUST preserve the controller restart envelope
- **AND** the bridge MUST NOT schedule automatic backoff, run a supervisor loop, infer ownership from port state, or change SSE/event-stream behavior.
