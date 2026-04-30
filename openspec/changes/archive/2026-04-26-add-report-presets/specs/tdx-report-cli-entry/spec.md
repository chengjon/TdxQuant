## ADDED Requirements

### Requirement: Report CLI SHALL expose a preset catalog
The system SHALL expose a CLI entry that lists available report presets defined in runtime configuration.

#### Scenario: Caller lists available presets
- **WHEN** a caller executes the report preset listing command
- **THEN** the system MUST return the available preset names together with their mapped report command metadata

### Requirement: Report CLI SHALL execute named presets through existing report workflows
The system SHALL allow callers to execute a named report preset that resolves to one supported report workflow plus default arguments.

#### Scenario: Caller runs a configured daily preset
- **WHEN** a caller executes a named preset whose target command is `daily`
- **THEN** the system MUST resolve the preset defaults and run the existing daily trade report workflow through the shared report dispatcher

#### Scenario: Explicit CLI arguments override preset defaults
- **WHEN** a caller executes a named preset and also provides overlapping CLI arguments explicitly
- **THEN** the system MUST prefer the explicit CLI argument values over the preset defaults

#### Scenario: Preset points to an unsupported command
- **WHEN** a caller executes a preset whose configured target is not a supported report command
- **THEN** the system MUST reject the request with an invalid-request style error instead of dispatching an unknown workflow
