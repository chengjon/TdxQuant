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

### Requirement: Trade submit-once CLI SHALL expose explicit order side

The stable submit-once CLI entry SHALL make the requested order side explicit while preserving the existing buy default and buy-only flat compatibility command.

#### Scenario: Caller runs submit-once with explicit sell side

- **WHEN** a caller executes `trade submit-once --side sell`
- **THEN** the CLI MUST build the stable submit-once request with sell side
- **AND** it MUST still use the submit-once execution mode
- **AND** it MUST keep existing safety controls such as `submission_key` and `max_price`

#### Scenario: Caller omits submit-once side

- **WHEN** a caller executes `trade submit-once` without `--side`
- **THEN** the CLI MUST preserve the previous buy-side default

#### Scenario: Caller uses the flat buy submit-once compatibility command

- **WHEN** a caller executes `pingan-buy-submit-once`
- **THEN** the command MUST remain buy-only by name
- **AND** the new side selector MUST NOT be required for that legacy command

### Requirement: Trade CLI SHALL expose a stable sell subcommand

The stable nested trade CLI SHALL expose Ping An sell through the dedicated `trade` command group rather than relying only on generic order placement or manager internals.

#### Scenario: Caller uses nested trade sell command

- **WHEN** a caller executes `trade sell`
- **THEN** the CLI MUST dispatch a stable sell request through the trade service path
- **AND** the request MUST use sell side
- **AND** the command MUST accept the same stable safety controls as `trade buy`

#### Scenario: Caller uses trade sell with safety controls

- **WHEN** a caller executes `trade sell` with `submission_key` or `max_price`
- **THEN** those controls MUST be forwarded unchanged to the stable sell workflow

### Requirement: Trade CLI SHALL expose a PingAn lifecycle owner lock subcommand

The stable desktop trade CLI SHALL expose a nested `trade lifecycle-owner-lock` subcommand for explicit local PingAn lifecycle owner lock operations.

#### Scenario: Caller parses lifecycle owner lock status command

- **WHEN** a caller parses `trade lifecycle-owner-lock --action status --statefile-path <path> --owner-token <token>`
- **THEN** the parser SHALL set `trade_command=lifecycle-owner-lock`
- **AND** it SHALL expose `action`, `statefile_path`, `owner_token`, `stale_after_seconds`, and `force_stale` arguments.

#### Scenario: Caller dispatches lifecycle owner lock command

- **WHEN** a caller dispatches `trade lifecycle-owner-lock`
- **THEN** the CLI SHALL call `TdxTradeManager.pingan.lifecycle_owner_lock(...)`
- **AND** it SHALL forward action, statefile path, owner token, stale timeout, and forced stale replacement.

#### Scenario: Lifecycle owner lock CLI remains explicit operator statefile control

- **WHEN** a caller uses `trade lifecycle-owner-lock`
- **THEN** the CLI SHALL NOT submit orders, run catalog workflows, start or stop the PingAn desktop process, restart, kill, supervise, or execute backoff.

### Requirement: Trade preflight CLI SHALL accept lifecycle owner lock status inputs

The stable `trade preflight` CLI SHALL accept optional inputs for a read-only PingAn lifecycle owner lock status check.

#### Scenario: Caller provides lifecycle owner lock status inputs to trade preflight

- **WHEN** a caller executes `trade preflight` with `--lifecycle-statefile-path`, `--lifecycle-owner-token`, and `--lifecycle-stale-after-seconds`
- **THEN** the CLI MUST parse those arguments
- **AND** the resolved preflight workflow MUST receive those values unchanged.

#### Scenario: Trade preflight CLI owner lock inputs remain read-only

- **WHEN** a caller executes `trade preflight` with lifecycle owner lock status inputs
- **THEN** the CLI MUST dispatch `TdxTradeManager.pingan.preflight(...)`
- **AND** it MUST NOT dispatch `TdxTradeManager.pingan.lifecycle_owner_lock(...)` with `action=acquire` or `action=release`.

### Requirement: Trade preflight CLI SHALL accept lifecycle owner lock requirement flag

The stable `trade preflight` CLI SHALL accept an opt-in flag requiring local PingAn lifecycle owner lock ownership during read-only preflight.

#### Scenario: Caller requires lifecycle owner lock during trade preflight

- **WHEN** a caller executes `trade preflight --require-lifecycle-owner-lock` with lifecycle owner lock status inputs
- **THEN** the CLI MUST parse the flag
- **AND** the resolved preflight workflow MUST receive `require_lifecycle_owner_lock=true`.

#### Scenario: Requirement flag does not dispatch lifecycle control

- **WHEN** a caller executes `trade preflight --require-lifecycle-owner-lock`
- **THEN** the CLI MUST still dispatch `TdxTradeManager.pingan.preflight(...)`
- **AND** it MUST NOT acquire or release the lifecycle owner lock.

### Requirement: Stable trade execution CLI SHALL accept lifecycle owner-lock guard arguments

The stable `trade buy`, `trade sell`, and `trade submit-once` CLI commands SHALL accept optional lifecycle owner-lock guard arguments.

#### Scenario: Caller requires lifecycle owner lock during stable trade execution

- **WHEN** a caller executes `trade buy`, `trade sell`, or `trade submit-once` with `--require-lifecycle-owner-lock`, `--lifecycle-statefile-path`, `--lifecycle-owner-token`, and `--lifecycle-stale-after-seconds`
- **THEN** the CLI MUST parse those arguments
- **AND** the resolved PingAn desktop gateway MUST receive those values unchanged.

#### Scenario: Stable execution CLI guard does not dispatch lifecycle control

- **WHEN** a caller executes a stable trade execution CLI command with `--require-lifecycle-owner-lock`
- **THEN** the CLI MUST still dispatch the normal trade execution path
- **AND** it MUST NOT dispatch lifecycle owner lock acquire or release.

### Requirement: Trade CLI SHALL expose PingAn lifecycle supervisor control subcommands

The stable desktop trade CLI SHALL expose explicit PingAn lifecycle supervisor control entrypoints for one-shot tick and bounded foreground run operations.

#### Scenario: CLI parses a supervisor tick command

- **WHEN** a caller parses `trade lifecycle-supervisor-tick --statefile-path <path> --owner-token <token>`
- **THEN** the parser MUST route the command to the trade subcommand dispatcher as `trade_command=lifecycle-supervisor-tick`
- **AND** the parsed arguments MUST preserve statefile path, owner token, stale timeout, restart-attempt limit, and backoff settings.

#### Scenario: CLI parses a bounded supervisor run command

- **WHEN** a caller parses `trade lifecycle-supervisor-run --statefile-path <path> --owner-token <token> --max-ticks <N>`
- **THEN** the parser MUST route the command to the trade subcommand dispatcher as `trade_command=lifecycle-supervisor-run`
- **AND** the parsed arguments MUST preserve statefile path, owner token, max tick count, interval, stale timeout, restart-attempt limit, and backoff settings.

#### Scenario: CLI dispatch remains explicit lifecycle control only

- **WHEN** the trade CLI dispatches either supervisor command
- **THEN** it MUST call the corresponding PingAn manager lifecycle supervisor method
- **AND** it MUST NOT dispatch buy, sell, submit-once, task, report, catalog, or bundle workflow execution.

### Requirement: Trade CLI SHALL expose PingAn process lifecycle control

The stable desktop trade CLI SHALL expose an explicit PingAn process lifecycle control entrypoint.

#### Scenario: CLI parses process lifecycle control

- **WHEN** a caller parses `trade lifecycle-process --action start --statefile-path <path> --owner-token <token> --exe-path <path>`
- **THEN** the parser MUST route the command to `trade_command=lifecycle-process`
- **AND** the parsed arguments MUST preserve action, statefile path, owner token, stale timeout, executable path, and force restart flag.

#### Scenario: CLI dispatches only lifecycle process control

- **WHEN** the trade CLI dispatches `trade lifecycle-process`
- **THEN** it MUST call the PingAn lifecycle process manager method
- **AND** it MUST NOT dispatch buy, sell, submit-once, task, report, catalog, or bundle workflow execution.

