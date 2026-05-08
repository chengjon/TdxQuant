# tdx-provider-capability-discovery Specification

## Purpose
TBD - created by archiving change add-provider-capability-discovery. Update Purpose after archive.
## Requirements
### Requirement: Provider capability discovery SHALL expose a canonical capability registry
The system SHALL expose a provider-facing capability registry that lists canonical TdxQuant capabilities with stable naming and grading metadata so upstream callers can determine what the provider exposes before invoking runtime actions.

#### Scenario: Capability discovery returns stable metadata for exposed capabilities
- **WHEN** a caller requests provider capability discovery
- **THEN** the response MUST include a structured list of exposed capabilities
- **AND** each capability entry MUST include a canonical capability name, capability version, stability grade, side-effect grade, and entrypoint metadata
- **AND** capability grading literals MUST use fixed values rather than free-form text

### Requirement: Provider capability discovery SHALL separate static registry data from runtime health state
The system SHALL keep capability registry metadata distinct from live environment health checks so callers can cache or inspect the exposed capability surface without requiring live TongDaXin runtime probes.

#### Scenario: Capability discovery succeeds without live runtime health execution
- **WHEN** a caller requests provider capability discovery
- **THEN** the provider MUST be able to return registry metadata even if a live runtime probe is not executed as part of the same call
- **AND** live availability conclusions MUST remain the responsibility of `health` or `doctor` style responses

### Requirement: Provider health probe SHALL expose structured runtime check results
The system SHALL expose a provider-facing health probe that reports structured runtime checks for the current platform and key TongDaXin dependencies.

#### Scenario: Health probe returns normalized checks
- **WHEN** a caller requests provider health information
- **THEN** the response MUST include an `overall_status` field and a structured set of check results
- **AND** the checks MUST cover platform support, `tqcenter` availability, query runtime viability, subscription runtime viability, desktop window probing, and HID availability
- **AND** each check MUST use fixed status literals rather than free-form human-only summaries

### Requirement: Provider doctor SHALL expose actionable findings and recommended next actions
The system SHALL expose a provider-facing doctor response that translates health results into structured findings, severities, and recommended actions.

#### Scenario: Doctor response includes actionable findings
- **WHEN** a caller requests provider doctor information
- **THEN** the response MUST include structured findings with stable severity literals and machine-readable identifiers
- **AND** the response MUST include recommended next actions derived from the current health state
- **AND** the doctor response MUST preserve the underlying health context rather than replacing it with plain text

### Requirement: Provider diagnostics SHALL treat environment state separately from probe execution success
The system SHALL represent provider health quality inside structured data rather than relying solely on top-level command failure semantics.

#### Scenario: Health probe completes while environment is unavailable
- **WHEN** the provider health or doctor probe finishes successfully but detects an unhealthy or unavailable environment
- **THEN** the top-level response MUST still remain a structured successful diagnostic result
- **AND** the unhealthy state MUST be represented through `overall_status`, checks, findings, warnings, or recommended actions rather than by omitting the diagnostic payload

### Requirement: Provider capability discovery SHALL expose query metadata for covered query capabilities
The system SHALL expose stable query-oriented metadata for the covered `market`, `meta`, `financial`, and `transaction` capabilities so upstream callers can reason about their invocation shape before issuing requests.

#### Scenario: Capability discovery reports query shapes and replay support
- **WHEN** a caller requests provider capability discovery
- **THEN** each covered query capability entry MUST expose machine-readable `query_metadata`
- **AND** `query_metadata.query_shapes` MUST be a list of objects
- **AND** each shape object MUST include at least `query_kind` and `selectors`
- **AND** each covered query capability entry MUST indicate replay support within `query_metadata`

#### Scenario: Capability discovery reports field-selection support for covered queries
- **WHEN** a caller requests provider capability discovery
- **THEN** each covered query capability entry MUST indicate within `query_metadata` whether the capability supports explicit requested-field selection
- **AND** the entry MUST indicate that empty successful result sets are valid outcomes for query consumption

#### Scenario: Capability discovery shape captures residual selector knobs
- **WHEN** a covered query capability needs selector parameters that are not represented by shared query fields such as `symbol`, `symbols`, `date`, `date_range`, `market`, or `block_code`
- **THEN** the corresponding `query_metadata.query_shapes` entry MUST expose those residual knobs via a machine-readable `query_params` field name list

