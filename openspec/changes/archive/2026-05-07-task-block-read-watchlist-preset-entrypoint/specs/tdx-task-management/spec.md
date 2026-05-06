## ADDED Requirements

### Requirement: Task preset execution SHALL support static block read watchlist presets
The system SHALL allow the existing task preset layer to target `block-read-watchlist` so daily callers can reuse a fixed `block_code` default for the stable snapshot task without retyping the full command.

#### Scenario: Caller runs a block read watchlist preset
- **WHEN** a caller executes a named task preset whose target command is `block-read-watchlist`
- **THEN** the system MUST resolve the preset defaults and run the existing stable block-read-watchlist workflow through the task-management path

#### Scenario: Explicit block read watchlist preset CLI arguments override preset defaults
- **WHEN** a caller executes a `block-read-watchlist` preset and also provides an explicit `block_code` CLI argument
- **THEN** the system MUST prefer that explicit CLI argument value over the preset default

#### Scenario: Block read watchlist preset is missing required fields
- **WHEN** a caller executes a `block-read-watchlist` preset that omits `block_code`
- **THEN** the system MUST reject the request as invalid instead of dispatching an incomplete snapshot workflow
