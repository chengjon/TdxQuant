## Purpose

定义桌面自动化交易的 `trade` CLI 入口层，包括稳定交易子命令、兼容旧扁平命令和可维护的 trade preset 快捷调用能力。
## Requirements
### Requirement: Desktop trading CLI SHALL evolve toward a dedicated nested trade command group
The system SHALL define desktop automation trading CLI standardization around a dedicated nested `trade` command group rather than extending the query-oriented `api` command group.

#### Scenario: Future nested trading CLI is introduced
- **WHEN** the project introduces a standardized nested CLI entry for desktop trading
- **THEN** that entry MUST be represented as a `trade` command group or an equivalently dedicated trading namespace

#### Scenario: Trading commands are not merged into api namespace
- **WHEN** a desktop trading command is standardized at the CLI layer
- **THEN** it MUST NOT require callers to use the query-oriented `api` namespace

#### Scenario: Caller uses nested trade buy command
- **WHEN** a caller executes the stable Ping An desktop buy workflow from the standardized CLI layer
- **THEN** the system MUST expose that workflow through a nested `trade buy` style command

#### Scenario: Caller uses nested trade submit-once command
- **WHEN** a caller executes the stable Ping An submit-once desktop workflow from the standardized CLI layer
- **THEN** the system MUST expose that workflow through a nested `trade submit-once` style command

### Requirement: Desktop trading CLI SHALL preserve flat-command compatibility during migration
The system SHALL preserve existing flat desktop trading commands while the future nested trade CLI is being planned and introduced.

#### Scenario: Existing flat trade command remains compatible
- **WHEN** the project defines the future `trade` CLI direction
- **THEN** existing flat commands such as `pingan-buy-submit-once`, `pingan-buy`, and related diagnostic commands MUST continue to operate during the migration period

#### Scenario: Stable and experimental commands can be separated later
- **WHEN** a future nested `trade` CLI is designed in detail
- **THEN** the system MAY separate stable trading commands from diagnostic or experimental commands without breaking the existing flat compatibility contract

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

### Requirement: Stable desktop trade CLI entrypoints SHALL expose safety-control arguments
The system SHALL expose stable safety-control arguments on the nested and flat stable desktop trade CLI entrypoints.

#### Scenario: Caller uses nested trade command with safety controls
- **WHEN** a caller executes `trade buy` or `trade submit-once`
- **THEN** the CLI MUST accept `submission_key`
- **AND** the CLI MUST accept `max_price`

#### Scenario: Caller uses flat compatibility command with safety controls
- **WHEN** a caller executes `pingan-buy` or `pingan-buy-submit-once`
- **THEN** the CLI MUST accept the same stable safety-control arguments as the nested trade commands

### Requirement: Trade preset execution SHALL preserve explicit safety-control overrides
The system SHALL allow preset-driven stable desktop trade execution to use preset safety defaults while still preferring explicit CLI overrides.

#### Scenario: Trade run forwards explicit safety controls
- **WHEN** a caller executes `trade run` with explicit safety-control arguments
- **THEN** the resolved stable trade workflow MUST receive those explicit values even if the preset defines different defaults

### Requirement: Trade CLI SHALL expose a stable health subcommand
The system SHALL expose a stable nested `trade health` CLI entrypoint for the read-only desktop trade health workflow.

#### Scenario: Caller uses nested trade health command
- **WHEN** a caller executes `trade health`
- **THEN** the CLI MUST dispatch the stable desktop trade health workflow

#### Scenario: Caller requests HID ping through trade health command
- **WHEN** a caller executes `trade health` with a HID `port`
- **THEN** the CLI MUST accept `port`, `baudrate`, `timeout`, and `pre_delay`
- **AND** the resolved health workflow MUST receive those values unchanged

### Requirement: Trade CLI SHALL expose a stable preflight subcommand
The system SHALL expose a stable nested `trade preflight` CLI entrypoint for the read-only desktop trade preflight workflow.

#### Scenario: Caller uses nested trade preflight command
- **WHEN** a caller executes `trade preflight`
- **THEN** the CLI MUST dispatch the stable desktop trade preflight workflow

#### Scenario: Caller provides stable trade safety controls to preflight
- **WHEN** a caller executes `trade preflight` with `submission_key` or `max_price`
- **THEN** the CLI MUST accept those arguments
- **AND** the resolved preflight workflow MUST receive those values unchanged

### Requirement: Trade CLI SHALL expose a stable dialog-readiness subcommand
The system SHALL expose a stable nested `trade dialog-readiness` CLI entrypoint for the read-only desktop trade dialog readiness workflow.

#### Scenario: Caller uses nested trade dialog-readiness command
- **WHEN** a caller executes `trade dialog-readiness`
- **THEN** the CLI MUST dispatch the stable desktop trade dialog readiness workflow

#### Scenario: Caller selects dialog target and visibility semantics
- **WHEN** a caller executes `trade dialog-readiness`
- **THEN** the CLI MUST accept a dialog target selector
- **AND** the CLI MUST accept `require_visible`
- **AND** the resolved workflow MUST receive those values unchanged

### Requirement: Trade CLI SHALL expose a stable submit-ready subcommand
The system SHALL expose a stable nested `trade submit-ready` CLI entrypoint for the pre-confirm desktop trade boundary workflow.

#### Scenario: Caller uses nested trade submit-ready command
- **WHEN** a caller executes `trade submit-ready`
- **THEN** the CLI MUST dispatch the stable desktop trade submit-ready workflow

#### Scenario: Caller provides boundary and safety controls to submit-ready
- **WHEN** a caller executes `trade submit-ready`
- **THEN** the CLI MUST accept `max_price`
- **AND** the CLI MUST accept confirm lookup boundary controls such as `dialog_lookup_mode` and `confirm_timeout`
- **AND** the resolved workflow MUST receive those values unchanged

### Requirement: Trade CLI SHALL expose a stable confirm-current subcommand
The system SHALL expose a stable nested `trade confirm-current` CLI entrypoint for the current-confirm desktop trade workflow.

#### Scenario: Caller uses nested trade confirm-current command
- **WHEN** a caller executes `trade confirm-current`
- **THEN** the CLI MUST dispatch the stable desktop trade confirm-current workflow

#### Scenario: Caller provides current-confirm boundary controls
- **WHEN** a caller executes `trade confirm-current`
- **THEN** the CLI MUST accept confirm/result boundary controls such as `dialog_lookup_mode`, `confirm_timeout`, `result_timeout`, and `close_result_dialog`
- **AND** the resolved workflow MUST receive those values unchanged

### Requirement: Trade CLI SHALL expose a stable broker-capabilities subcommand
The system SHALL expose a stable nested `trade broker-capabilities` CLI entrypoint for the non-executing PingAn desktop extended broker capability probe.

#### Scenario: Caller uses nested trade broker-capabilities command
- **WHEN** a caller executes `trade broker-capabilities`
- **THEN** the CLI MUST dispatch the extended broker capability probe
- **AND** the command MUST NOT execute funds query, positions query, cancel order, or broker-native push subscription

#### Scenario: Caller selects PingAn desktop broker capability boundary
- **WHEN** a caller executes `trade broker-capabilities --broker pingan_desktop`
- **THEN** the CLI MUST return PingAn desktop capability metadata
- **AND** the command MUST reject unsupported broker names rather than falling back to another broker

