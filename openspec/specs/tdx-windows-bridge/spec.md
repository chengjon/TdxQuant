# tdx-windows-bridge Specification

## Purpose

定义 Windows 侧桥接边界和 JSON 结果契约，使 WSL 侧调用能够安全委派 Win32、UIA、TongDaXin API 和 HID 操作。

## Requirements
### Requirement: Windows bridge SHALL provide a unified health check
The system SHALL provide a Windows-side bridge entrypoint that reports whether the bridge runtime, the TongDaXin client, and optional HID hardware prerequisites are available for use by WSL-side callers.

#### Scenario: Bridge health check succeeds
- **WHEN** a caller invokes the bridge health check from a supported Windows Python environment
- **THEN** the system returns structured JSON containing bridge status, platform information, and TongDaXin process/window availability

#### Scenario: Bridge health check runs on unsupported platform
- **WHEN** a caller invokes the bridge health check from WSL or Linux instead of native Windows Python
- **THEN** the system returns a structured unsupported-platform error with a next action explaining to run the command from Windows Python

### Requirement: Windows bridge SHALL expose JSON-stable command results
The system SHALL return a stable JSON result envelope for bridge commands so that WSL-side scripts do not need to parse plain text output.

#### Scenario: Bridge command succeeds
- **WHEN** a bridge command completes successfully
- **THEN** the system returns a JSON object containing `ok`, `code`, `message`, and `data`

#### Scenario: Bridge command needs operator guidance
- **WHEN** a bridge command cannot continue automatically because a prerequisite is missing
- **THEN** the system returns `warnings` and `next_action` fields describing the missing prerequisite

### Requirement: Windows bridge SHALL define a WSL-safe invocation boundary
The system SHALL keep all Win32, UIA, TdxQuant Windows API, and HID operations on the Windows side of the bridge boundary.

#### Scenario: WSL caller requests a Windows-only operation
- **WHEN** a WSL-side script requests a TongDaXin desktop operation through the bridge
- **THEN** the operation is executed by Windows-native code rather than directly from WSL

#### Scenario: Windows-only dependency is unavailable
- **WHEN** the Windows-side runtime is missing a required dependency such as `pywin32` or `pyserial`
- **THEN** the bridge returns a structured execution error identifying the missing dependency
