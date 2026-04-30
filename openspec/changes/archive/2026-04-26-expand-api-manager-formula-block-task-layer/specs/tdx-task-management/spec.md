## ADDED Requirements

### Requirement: Task management SHALL provide a stable scenario-oriented entry layer above API manager
The system SHALL define a task layer above `TdxApiManager` for stable, scenario-oriented daily workflows rather than requiring users to compose raw API calls each time.

#### Scenario: Task composes multiple manager domains
- **WHEN** a daily workflow requires multiple API steps across domains
- **THEN** the task layer MUST be able to orchestrate calls across manager domains such as `market`, `meta`, `formula`, and `block`

#### Scenario: Task layer does not bypass manager
- **WHEN** a task is implemented
- **THEN** it MUST use manager-level domain methods rather than calling `bridge.py` directly

### Requirement: Task management SHALL stay focused on stable high-frequency workflows
The system SHALL restrict the task layer to stable, repeatable daily workflows instead of turning it into a container for arbitrary one-off scripts.

#### Scenario: Stable workflow is added as a task
- **WHEN** a new task capability is introduced
- **THEN** it MUST represent a repeatable scenario such as sector research, formula scanning, watchlist refresh, or environment maintenance

#### Scenario: One-off experiment is proposed as a task
- **WHEN** a workflow is ad hoc or experimental
- **THEN** it MUST NOT be required to enter the task layer as a permanent task capability

### Requirement: Task management SHALL support dedicated task profiles
The system SHALL support task-specific profiles separately from raw API profiles so that stable workflows can carry their own output, export, and batching defaults.

#### Scenario: Caller invokes a task with a named task profile
- **WHEN** a caller requests a task using a task profile
- **THEN** the task layer MUST resolve task-scoped defaults independently from the raw API profile file

#### Scenario: Task internally uses API manager
- **WHEN** a task executes manager-backed API calls
- **THEN** the task layer MAY map task-level defaults into manager-level profile settings or explicit per-call overrides
