## ADDED Requirements

### Requirement: Task preset execution SHALL support static block read watchlist export presets
The system SHALL allow the existing task preset layer to target `block-read-watchlist-export` so daily callers can reuse fixed export defaults without retyping the full command.

#### Scenario: Caller runs a block read watchlist export preset
- **WHEN** a caller executes a named task preset whose target command is `block-read-watchlist-export`
- **THEN** the system MUST resolve the preset defaults and run the existing stable block-read-watchlist-export workflow through the task-management path

#### Scenario: Explicit export preset CLI arguments override preset defaults
- **WHEN** a caller executes a `block-read-watchlist-export` preset and also provides explicit `block_code`, `export_output`, or `overwrite` CLI arguments
- **THEN** the system MUST prefer those explicit CLI argument values over the preset defaults

#### Scenario: Export preset is missing required fields
- **WHEN** a caller executes a `block-read-watchlist-export` preset that omits `block_code` or `export_output`
- **THEN** the system MUST reject the request as invalid instead of dispatching an incomplete export workflow
