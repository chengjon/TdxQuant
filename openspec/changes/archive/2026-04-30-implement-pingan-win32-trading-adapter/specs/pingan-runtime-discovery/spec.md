## ADDED Requirements

### Requirement: Runtime MUST resolve the Ping An Securities executable path
The system SHALL resolve the Ping An Securities client executable from explicit configuration or supported default locations before any window inspection or trade action is attempted.

#### Scenario: Explicit Windows path is provided
- **WHEN** the operator provides `D:\ProgramData\PinganSec\TdxW.exe` as the configured executable path
- **THEN** the system SHALL validate that the file exists and mark it as the active runtime path

#### Scenario: WSL-mapped path is provided
- **WHEN** the operator provides `/mnt/d/ProgramData/PinganSec/TdxW.exe` as the configured executable path
- **THEN** the system SHALL validate that the file exists and expose it as the resolved installation path in command results

#### Scenario: No explicit path is provided
- **WHEN** the operator runs a discovery or health-check command without an explicit executable path
- **THEN** the system SHALL search supported default Ping An Securities installation paths and return the first validated path

### Requirement: Runtime discovery MUST fail safely
The system SHALL refuse to continue to window inspection or order entry when no valid Ping An Securities executable path can be resolved.

#### Scenario: No supported path can be validated
- **WHEN** discovery cannot validate any explicit or default executable path
- **THEN** the system SHALL return a structured failure result with the attempted paths and a next action for the operator

### Requirement: Runtime discovery MUST report path provenance
The system SHALL report how the executable path was resolved so operators can distinguish between configured and auto-detected runtime paths.

#### Scenario: Path came from auto-detection
- **WHEN** the system resolves `/mnt/d/ProgramData/PinganSec/TdxW.exe` through default path probing
- **THEN** the result SHALL indicate that the active runtime path source is auto-detected rather than explicitly configured
