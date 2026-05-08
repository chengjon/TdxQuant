## ADDED Requirements

### Requirement: Trade CLI SHALL expose stable PingAn sell entrypoints parallel to existing buy entrypoints
The system SHALL expose stable nested `trade` CLI commands for `PingAn` sell execution without changing the current buy command semantics.

#### Scenario: Caller uses nested trade sell command
- **WHEN** a caller executes the stable `PingAn` desktop sell workflow from the nested trade CLI
- **THEN** the system MUST expose that workflow through a dedicated `trade sell` command

#### Scenario: Caller uses nested trade sell-submit-once command
- **WHEN** a caller executes the stable `PingAn` desktop sell workflow that advances through HID submit and confirmation
- **THEN** the system MUST expose that workflow through a dedicated `trade sell-submit-once` command

### Requirement: Trade preset execution SHALL support sell-oriented PingAn live workflows
The system SHALL allow trade preset execution to target both stable sell and stable sell-submit-once workflows while preserving explicit CLI overrides.

#### Scenario: Caller runs a configured sell preset
- **WHEN** a caller executes a named trade preset whose target command is `sell`
- **THEN** the system MUST resolve the preset defaults and run the existing stable trade sell workflow

#### Scenario: Caller runs a configured sell-submit-once preset
- **WHEN** a caller executes a named trade preset whose target command is `sell-submit-once`
- **THEN** the system MUST resolve the preset defaults and run the existing stable sell submit-once workflow
