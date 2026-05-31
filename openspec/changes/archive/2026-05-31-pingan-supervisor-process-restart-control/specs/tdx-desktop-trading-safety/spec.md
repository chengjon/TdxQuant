## ADDED Requirements

### Requirement: PingAn supervisor process restart SHALL remain explicit lifecycle control evidence

PingAn supervisor process restart integration SHALL remain explicit lifecycle control evidence and MUST NOT imply trading readiness or broad process ownership.

#### Scenario: Supervisor process restart boundary remains explicit

- **WHEN** supervisor process restart opt-in is enabled
- **THEN** returned evidence MUST state that process restart is delegated to the recorded-PID guarded lifecycle process controller
- **AND** returned evidence MUST include `order_submitted=false`
- **AND** returned evidence MUST not claim broker readiness, UI login readiness, retry/resubmit readiness, or live/manual acceptance.
