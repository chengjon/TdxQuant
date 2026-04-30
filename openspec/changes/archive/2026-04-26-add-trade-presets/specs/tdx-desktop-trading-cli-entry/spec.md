## ADDED Requirements

### Requirement: Trade CLI SHALL expose a preset catalog
The system SHALL expose a CLI entry that lists available trade presets defined in runtime configuration.

#### Scenario: Caller lists available trade presets
- **WHEN** a caller executes the trade preset listing command
- **THEN** the system MUST return the available preset names together with their mapped stable trade command metadata

### Requirement: Trade CLI SHALL execute named presets through stable trade workflows
The system SHALL allow callers to execute a named trade preset that resolves to one supported stable trade workflow plus default command arguments.

#### Scenario: Caller runs a configured buy preset
- **WHEN** a caller executes a named trade preset whose target command is `buy`
- **THEN** the system MUST resolve the preset defaults and run the existing stable trade buy workflow

#### Scenario: Caller runs a configured submit-once preset
- **WHEN** a caller executes a named trade preset whose target command is `submit-once`
- **THEN** the system MUST resolve the preset defaults and run the existing stable trade submit-once workflow

#### Scenario: Explicit CLI arguments override trade preset defaults
- **WHEN** a caller executes a named trade preset and also provides overlapping CLI arguments explicitly
- **THEN** the system MUST prefer the explicit CLI argument values over the preset defaults

#### Scenario: Trade preset points to an unsupported command
- **WHEN** a caller executes a trade preset whose configured target is not a supported stable trade command
- **THEN** the system MUST reject the request with an invalid-request style error instead of dispatching an unknown workflow
