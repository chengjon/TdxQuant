## ADDED Requirements

### Requirement: Desktop trading management SHALL define PingAn plus HID as the active live-trading execution mainline
The system SHALL treat `PingAn` desktop execution with HID-backed final submit actions as the only active live-trading mainline for desktop trading workflows.

#### Scenario: Live-trading scope excludes TongDaXin execution
- **WHEN** the project defines the current live desktop trading path
- **THEN** the active execution baseline MUST be `PingAn` desktop plus HID
- **AND** `TongDaXin` trading MUST NOT be required for live execution closure

#### Scenario: PingAn live workflow persists through the standard finalized path
- **WHEN** a stable `PingAn` live trade completes through the management layer
- **THEN** the workflow MUST continue to use the standard finalized persistence path for audit, state, and event artifacts

### Requirement: Desktop trading management SHALL expose stable PingAn sell workflows alongside existing buy workflows
The system SHALL expose stable `PingAn` sell workflows that mirror the current buy workflows across both the fast path and the full submit-once path.

#### Scenario: Caller executes fast sell through the management layer
- **WHEN** a caller requests a stable `PingAn` sell workflow through the desktop trading management path
- **THEN** the system MUST support a finalized sell execution path analogous to the existing stable buy path

#### Scenario: Caller executes sell submit-once through the management layer
- **WHEN** a caller requests a stable `PingAn` sell workflow that advances through HID submit, confirmation, and result dialog handling
- **THEN** the system MUST support a finalized `sell_submit_once` execution path
- **AND** that workflow MUST preserve the same safety controls and finalized artifact governance already used by the existing buy submit-once path
