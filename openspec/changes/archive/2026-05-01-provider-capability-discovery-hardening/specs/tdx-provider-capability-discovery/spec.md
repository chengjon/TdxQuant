## ADDED Requirements

### Requirement: Provider diagnostics SHALL expose structured recommended action items alongside compatibility strings
The system SHALL expose machine-readable recommended action rows for provider diagnostics while preserving the existing human-readable compatibility list.

#### Scenario: Health or doctor response includes structured action rows
- **WHEN** a caller requests provider health or doctor information and one or more checks are not fully healthy
- **THEN** the `data` payload MUST include `recommended_action_items`
- **AND** each item MUST include a stable machine-readable `id`, a human-readable `summary`, a stable `severity`, and `related_checks`
- **AND** the legacy `recommended_actions` string list MAY remain present as a compatibility projection of those structured action rows

## MODIFIED Requirements

### Requirement: Provider capability discovery SHALL expose a canonical capability registry
The system SHALL expose a provider-facing capability registry that lists canonical TdxQuant capabilities with stable naming and grading metadata so upstream callers can determine what the provider exposes before invoking runtime actions.

#### Scenario: Capability discovery returns stable metadata for exposed capabilities
- **WHEN** a caller requests provider capability discovery
- **THEN** the response MUST use the hardened synchronous provider result envelope
- **AND** the `data` payload MUST include a structured list of exposed capabilities
- **AND** each capability entry MUST include a canonical capability name, capability version, stability grade, side-effect grade, and entrypoint metadata
- **AND** the `data` payload MUST also include a stable `summary` object and a stable `grading` object for registry-level aggregation metadata
- **AND** capability grading literals MUST use fixed values rather than free-form text

### Requirement: Provider health probe SHALL expose structured runtime check results
The system SHALL expose a provider-facing health probe that reports structured runtime checks for the current platform and key TongDaXin dependencies.

#### Scenario: Health probe returns normalized checks
- **WHEN** a caller requests provider health information
- **THEN** the response MUST use the hardened synchronous provider result envelope
- **AND** the `data` payload MUST include `overall_status`, `context`, `checks`, `recommended_actions`, `recommended_action_items`, `warning_count`, and `warnings`
- **AND** the `context` object MUST include the effective `window_key`, `strategy_path`, and requested HID port metadata
- **AND** the checks MUST cover platform support, `tqcenter` availability, query runtime viability, subscription runtime viability, desktop window probing, and HID availability
- **AND** each check MUST use fixed status literals rather than free-form human-only summaries

### Requirement: Provider doctor SHALL expose actionable findings and recommended next actions
The system SHALL expose a provider-facing doctor response that translates health results into structured findings, severities, and recommended actions.

#### Scenario: Doctor response includes actionable findings
- **WHEN** a caller requests provider doctor information
- **THEN** the response MUST use the hardened synchronous provider result envelope
- **AND** the `data` payload MUST include structured findings with stable severity literals and machine-readable identifiers
- **AND** each finding MUST include a stable machine-readable `id`, `severity`, `status`, `summary`, and `critical` flag
- **AND** a finding MAY include structured linkage to related checks or recommended action identifiers
- **AND** the response MUST include recommended next actions derived from the current health state
- **AND** the doctor response MUST preserve the underlying health context rather than replacing it with plain text

### Requirement: Provider diagnostics SHALL treat environment state separately from probe execution success
The system SHALL represent provider health quality inside structured data rather than relying solely on top-level command failure semantics.

#### Scenario: Health probe completes while environment is unavailable
- **WHEN** the provider health or doctor probe finishes successfully but detects an unhealthy or unavailable environment
- **THEN** the top-level response MUST still remain a structured successful diagnostic result
- **AND** `success` and `ok` MUST both remain `true`
- **AND** the unhealthy state MUST be represented through `overall_status`, checks, findings, warnings, recommended actions, or structured action rows rather than by omitting the diagnostic payload
