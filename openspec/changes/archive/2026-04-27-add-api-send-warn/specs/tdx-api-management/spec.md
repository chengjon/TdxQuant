## ADDED Requirements

### Requirement: Query API management SHALL expose client warn sending through the runtime domain
The system SHALL expose client warn sending through the existing `runtime` domain on `TdxApiManager` instead of placing it inside `market` or introducing a separate top-level manager action.

#### Scenario: Caller sends warn payload through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke client warn sending through `manager.runtime.send_warn(...)`

### Requirement: Query API management SHALL keep client warn payloads explicit and profile-agnostic
The system SHALL keep `send_warn` payload construction independent from profile file loading and SHALL require the caller to pass warn batch lists explicitly instead of resolving default payload lists from API profile defaults.

#### Scenario: Runtime domain delegates warn payload without reading profile files
- **WHEN** a manager-driven warn send is invoked
- **THEN** the `runtime` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Warn payload lists are not inferred from API profile defaults
- **WHEN** a caller invokes `manager.runtime.send_warn(...)`
- **THEN** the manager MUST use the explicitly provided warn payload lists rather than resolving default payload lists from the selected API profile

### Requirement: Query API management SHALL preserve official warn count semantics
The system SHALL preserve the official runtime behavior that `count` limits the number of effective entries in each warn payload list.

#### Scenario: Caller sends warn payload with explicit count
- **WHEN** a caller invokes `manager.runtime.send_warn(...)` with an explicit `count`
- **THEN** the manager MUST pass that `count` value through unchanged to the bridge layer
