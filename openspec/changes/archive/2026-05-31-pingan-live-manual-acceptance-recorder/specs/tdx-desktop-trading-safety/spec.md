## ADDED Requirements

### Requirement: PingAn manual acceptance recorder SHALL remain non-trading evidence capture

The PingAn live/manual acceptance recorder SHALL record operator-provided evidence only and SHALL NOT execute or infer trading workflows.

#### Scenario: Recorder boundary is explicit

- **WHEN** the recorder returns metadata
- **THEN** the metadata SHALL state that it does not execute PingAn workflows, submit orders, control the desktop, prove broker production readiness, or promote D-07/D-08 status.

