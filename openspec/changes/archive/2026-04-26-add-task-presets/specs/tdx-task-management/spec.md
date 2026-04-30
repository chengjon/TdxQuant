## ADDED Requirements

### Requirement: Task CLI SHALL expose a preset catalog for stable task workflows
The system SHALL expose a CLI entry that lists available task presets defined in runtime configuration.

#### Scenario: Caller lists available task presets
- **WHEN** a caller executes the task preset listing command
- **THEN** the system MUST return the available preset names together with their mapped stable task command metadata

### Requirement: Task CLI SHALL execute named presets through stable task workflows
The system SHALL allow callers to execute a named task preset that resolves to one supported stable task workflow plus default command arguments.

#### Scenario: Caller runs a configured guarded trade preset
- **WHEN** a caller executes a named task preset whose target command is `guarded-trade-buy`
- **THEN** the system MUST resolve the preset defaults and run the existing guarded trade workflow through the stable task management path

#### Scenario: Caller runs a configured refresh preset
- **WHEN** a caller executes a named task preset whose target command is `refresh-environment`
- **THEN** the system MUST resolve the preset defaults and run the existing refresh workflow through the stable task management path

#### Scenario: Explicit CLI arguments override task preset defaults
- **WHEN** a caller executes a named task preset and also provides overlapping CLI arguments explicitly
- **THEN** the system MUST prefer the explicit CLI argument values over the preset defaults

#### Scenario: Task preset points to an unsupported command
- **WHEN** a caller executes a task preset whose configured target is not a supported stable task preset command
- **THEN** the system MUST reject the request with an invalid-request style error instead of dispatching an unknown workflow
