## ADDED Requirements

### Requirement: Desktop trading management SHALL validate PingAn lifecycle owner PID liveness

The PingAn lifecycle owner lock payload SHALL include local owner PID liveness diagnostics when owner state is available.

#### Scenario: Caller checks owner lock status with alive owner PID

- **WHEN** a caller requests PingAn lifecycle owner lock `status` for a statefile that records an alive owner PID
- **THEN** the payload SHALL include `pid_validation_executed=true`
- **AND** the payload SHALL include the recorded `owner_pid`, `owner_pid_alive=true`, and `owner_pid_status=alive`.

#### Scenario: Caller checks owner lock status with missing owner PID

- **WHEN** a caller requests PingAn lifecycle owner lock `status` for a statefile without a valid owner PID
- **THEN** the payload SHALL include `pid_validation_executed=true`
- **AND** the payload SHALL include `owner_pid=null`, `owner_pid_alive=null`, and `owner_pid_status=missing`.

#### Scenario: Acquire and release expose owner PID diagnostics

- **WHEN** a caller acquires or releases a PingAn lifecycle owner lock
- **THEN** the returned payload SHALL include owner PID validation fields
- **AND** the payload SHALL keep `pid_ownership_claimed=false`.
