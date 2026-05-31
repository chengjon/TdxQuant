## ADDED Requirements

### Requirement: PingAn owner PID validation SHALL NOT imply desktop process ownership

PingAn lifecycle owner PID validation SHALL remain a local diagnostic for the owner lock statefile and SHALL NOT be treated as proof of real desktop process lifecycle ownership.

#### Scenario: Owner PID validation reports alive local process

- **WHEN** PingAn lifecycle owner lock payload reports `owner_pid_alive=true`
- **THEN** the payload MUST still report `pid_ownership_claimed=false`
- **AND** it MUST still report that no start, stop, restart, kill, supervisor ownership, backoff execution, order submission, or trade artifact write occurred.

#### Scenario: Owner PID validation is registered without implemented trading status

- **WHEN** D-07 or D-08 evidence includes PingAn owner PID validation
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that owner PID liveness is only a local statefile diagnostic, not real PingAn desktop process ownership or live/manual acceptance.
