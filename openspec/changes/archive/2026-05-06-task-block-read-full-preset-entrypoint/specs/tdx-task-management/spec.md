## ADDED Requirements

### Requirement: Task preset execution SHALL support static block read full presets
The system SHALL allow the existing task preset layer to target `block-read-full` so daily callers can reuse a fixed `block_code` default for the stable diagnostics task without retyping the full command.

#### Scenario: Caller runs a block read full preset
- **WHEN** a caller executes a named task preset whose target command is `block-read-full`
- **THEN** the system MUST resolve the preset defaults and run the existing stable block-read-full workflow through the task-management path

#### Scenario: Explicit block read full preset CLI arguments override preset defaults
- **WHEN** a caller executes a `block-read-full` preset and also provides an explicit `block_code` CLI argument
- **THEN** the system MUST prefer that explicit CLI argument value over the preset default

#### Scenario: Block read full preset is missing required fields
- **WHEN** a caller executes a `block-read-full` preset that omits `block_code`
- **THEN** the system MUST reject the request as invalid instead of dispatching an incomplete diagnostics workflow
