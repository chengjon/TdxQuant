## ADDED Requirements

### Requirement: Query API management SHALL provide a unified manager entrypoint
The system SHALL provide a `TdxApiManager` entrypoint for query-oriented TdxQuant capabilities so that callers do not need to invoke bridge functions directly for daily read workflows.

#### Scenario: Code caller uses manager to access market domain
- **WHEN** a caller imports the public API entrypoint and constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke query capabilities through `manager.market.<method>()`

#### Scenario: Code caller uses manager to access meta domain
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke metadata capabilities through `manager.meta.<method>()`

### Requirement: Query API management SHALL keep domain modules profile-agnostic
The system SHALL keep `market` and `meta` domain modules independent from profile file loading and top-level profile merge logic.

#### Scenario: Domain method receives standardized parameters
- **WHEN** a domain method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Domain layer remains bridge-based
- **WHEN** a domain method executes a query capability
- **THEN** it MUST call the corresponding bridge capability instead of reimplementing low-level runtime initialization

### Requirement: Query API management SHALL support API profiles with explicit override precedence
The system SHALL load query API profiles from `runtime/api-profiles.json` using an absolute path and SHALL apply explicit call-time overrides after loading the selected profile.

#### Scenario: Profile file is resolved without relying on current working directory
- **WHEN** the caller invokes manager logic from any working directory
- **THEN** the profile file path MUST be resolved from project-relative code location rather than from process current working directory

#### Scenario: Explicit arguments override profile defaults
- **WHEN** a selected profile provides default values and the caller also passes explicit parameter values
- **THEN** the explicit parameter values MUST take precedence over the profile defaults

### Requirement: Query API management SHALL attach standardized management metadata
The system SHALL add standardized management metadata for manager-driven calls, including selected profile identity and timing information.

#### Scenario: Manager-driven query returns profile metadata
- **WHEN** a manager-driven query completes
- **THEN** the result MUST include the effective API profile information used for the call

#### Scenario: Manager-driven query returns timing metadata
- **WHEN** a manager-driven query completes
- **THEN** the result MUST include timing data for the manager-managed execution flow

### Requirement: Query API management SHALL expose refresh cache as a manager action
The system SHALL expose `refresh_cache` as a direct manager action instead of placing it in the read-only `meta` domain.

#### Scenario: Caller refreshes market cache through manager
- **WHEN** a caller invokes the manager refresh-cache action with market and force parameters
- **THEN** the manager MUST delegate to the existing bridge refresh-cache capability and return standardized management metadata

#### Scenario: Refresh cache remains separate from read-only meta queries
- **WHEN** a caller accesses the `meta` domain
- **THEN** refresh-cache behavior MUST NOT be represented as a `meta` domain method
