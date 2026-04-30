## Purpose

定义面向日常复盘与交易排障的 `report` CLI 入口层，包括稳定报表子命令和可维护的 preset 快捷调用能力。
## Requirements
### Requirement: Report CLI SHALL provide a dedicated nested report command group
The system SHALL provide a dedicated nested `report` command group for stable ledger and trade-report inspection workflows.

#### Scenario: Caller uses report daily command
- **WHEN** a caller executes a supported daily trade report workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report daily` style command

#### Scenario: Caller uses report lookup command
- **WHEN** a caller executes a supported single-report lookup workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report lookup` style command

### Requirement: Report CLI SHALL preserve task-command compatibility during migration
The system SHALL keep existing report-related `task` commands functional while the dedicated `report` group is introduced.

#### Scenario: Existing task report command remains available
- **WHEN** a caller invokes an existing report-related `task` command during the expansion phase
- **THEN** that command MUST remain usable while the dedicated `report` group is being introduced

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

### Requirement: Report CLI SHALL expose a dedicated trade audit lookup command
The system SHALL expose a dedicated nested `report audit-lookup` command for stable inspection of immutable desktop trade audit artifacts.

#### Scenario: Caller uses report audit-lookup command
- **WHEN** a caller executes a supported trade audit lookup workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report audit-lookup` command

### Requirement: Report CLI SHALL expose dedicated trade audit daily and period commands
The system SHALL expose dedicated nested `report audit-daily` and `report audit-period` commands for stable inspection of aggregated desktop trade audit artifacts.

#### Scenario: Caller uses report audit-daily command
- **WHEN** a caller executes a supported trade audit daily report workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report audit-daily` command

#### Scenario: Caller uses report audit-period command
- **WHEN** a caller executes a supported trade audit period report workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report audit-period` command

### Requirement: Report CLI preset catalog SHALL expose audit-oriented review presets once trade audit reports are stable
The system SHALL expose stable report preset definitions for the existing trade audit daily and period workflows so callers can reuse common review defaults without retyping command arguments.

#### Scenario: Caller lists audit daily review presets
- **WHEN** a caller executes the report preset listing command after trade audit daily reporting is stable
- **THEN** the preset catalog MUST include at least one stable preset mapped to the audit daily workflow

#### Scenario: Caller runs an audit period preset
- **WHEN** a caller executes a named report preset mapped to the audit period workflow
- **THEN** the report CLI MUST resolve the preset defaults and run the existing audit period workflow through the shared report dispatcher

### Requirement: Report CLI SHALL expose rejected-oriented trade audit presets once stable trade audit reports support status filtering
The system SHALL expose stable report presets for rejected-oriented trade audit daily and period workflows so callers can reuse those diagnostics without retyping the same status filters.

#### Scenario: Caller lists rejected audit report presets
- **WHEN** a caller lists report presets after stable trade audit status filtering is available
- **THEN** the preset registry MUST include rejected-oriented presets for the existing trade audit daily and period workflows

#### Scenario: Caller runs a rejected audit report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `status=rejected`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path

### Requirement: Report CLI SHALL expose a richer stable trade-audit status preset matrix once status filtering is stable
The system SHALL expose additional stable report presets for confirmed-period and replayed-oriented trade-audit workflows so callers can reuse those review views without repeating the same status filters.

#### Scenario: Caller lists richer trade-audit status report presets
- **WHEN** a caller lists report presets after stable trade-audit status filtering is available
- **THEN** the preset registry MUST include presets for `audit-period-confirmed`, `audit-daily-replayed`, and `audit-period-replayed`

#### Scenario: Caller runs a richer trade-audit status report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `status=confirmed` or `status=replayed`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path

### Requirement: Report CLI SHALL expose failed-oriented stable trade-audit presets once failed status filtering is stable
The system SHALL expose stable report presets for failed-oriented trade-audit daily and period workflows so callers can reuse those diagnostics without repeating the same status filter.

#### Scenario: Caller lists failed-oriented trade-audit report presets
- **WHEN** a caller lists report presets after stable `status=failed` filtering is available for trade-audit reports
- **THEN** the preset registry MUST include failed-oriented presets for the existing trade-audit daily and period workflows

#### Scenario: Caller runs a failed-oriented trade-audit report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `status=failed`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path

### Requirement: Report and task CLI SHALL expose multi-status trade-audit filtering without breaking existing single-status calls
The system SHALL expose a stable CLI way to express multi-status trade-audit filtering for the existing daily and period workflows while preserving the current single-status option.

#### Scenario: Caller passes repeated multi-status arguments
- **WHEN** a caller invokes the stable trade-audit daily or period CLI workflow and repeats the multi-status argument
- **THEN** the CLI MUST forward the collected statuses into the existing stable workflow using OR semantics

#### Scenario: Caller mixes single-status and multi-status CLI arguments
- **WHEN** a caller invokes the stable trade-audit daily or period CLI workflow with both single-status and multi-status arguments
- **THEN** the CLI MUST reject the request as invalid instead of guessing precedence

### Requirement: Report CLI SHALL expose confirm-oriented exception trade-audit presets once multidimensional filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `method=confirm_current` together with `statuses=[rejected, failed]` so callers can reuse confirm-step exception diagnostics without retyping the same multidimensional filters.

#### Scenario: Caller lists confirm-oriented exception report presets
- **WHEN** a caller lists report presets after stable `method + statuses` trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-confirm-exceptions` and `audit-period-confirm-exceptions`

#### Scenario: Caller runs a confirm-oriented exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `method=confirm_current` and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path

### Requirement: Report CLI SHALL expose submit-once-oriented exception trade-audit presets once multidimensional filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `method=buy_submit_once` together with `statuses=[rejected, failed]` so callers can reuse full-submit exception diagnostics without retyping the same multidimensional filters.

#### Scenario: Caller lists submit-once-oriented exception report presets
- **WHEN** a caller lists report presets after stable `method + statuses` trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-submit-once-exceptions` and `audit-period-submit-once-exceptions`

#### Scenario: Caller runs a submit-once-oriented exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `method=buy_submit_once` and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path

### Requirement: Report CLI SHALL expose buy-oriented exception trade-audit presets once multidimensional filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `method=buy` together with `statuses=[rejected, failed]` so callers can reuse base-buy exception diagnostics without retyping the same multidimensional filters.

#### Scenario: Caller lists buy-oriented exception report presets
- **WHEN** a caller lists report presets after stable `method + statuses` trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-buy-exceptions` and `audit-period-buy-exceptions`

#### Scenario: Caller runs a buy-oriented exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `method=buy` and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path

### Requirement: Report and task CLI SHALL expose multi-method trade-audit filtering without breaking existing single-method calls
The system SHALL expose a stable CLI way to express multi-method trade-audit filtering for the existing daily and period workflows while preserving the current single-method option.

#### Scenario: Caller passes repeated multi-method arguments
- **WHEN** a caller invokes the stable trade-audit daily or period CLI workflow and repeats the multi-method argument
- **THEN** the CLI MUST forward the collected methods into the existing stable workflow using OR semantics

#### Scenario: Caller mixes single-method and multi-method CLI arguments
- **WHEN** a caller invokes the stable trade-audit daily or period CLI workflow with both single-method and multi-method arguments
- **THEN** the CLI MUST reject the request as invalid instead of guessing precedence

### Requirement: Report CLI SHALL expose submit-path exception presets once multi-method filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `methods=[buy_submit_once, confirm_current]` together with `statuses=[rejected, failed]` so callers can reuse submit-path exception diagnostics.

#### Scenario: Caller lists submit-path exception report presets
- **WHEN** a caller lists report presets after stable multi-method trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-submit-path-exceptions` and `audit-period-submit-path-exceptions`

#### Scenario: Caller runs a submit-path exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `methods=[buy_submit_once, confirm_current]` and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path

### Requirement: Report CLI SHALL expose broker-scoped submit-path exception presets once multidimensional broker filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `broker=pingan`, `methods=[buy_submit_once, confirm_current]`, and `statuses=[rejected, failed]` so callers can reuse broker-scoped submit-path exception diagnostics without retyping the same three-dimensional filter combination.

#### Scenario: Caller lists broker-scoped submit-path exception report presets
- **WHEN** a caller lists report presets after stable `broker + methods + statuses` trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-pingan-submit-path-exceptions` and `audit-period-pingan-submit-path-exceptions`

#### Scenario: Caller runs a broker-scoped submit-path exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `broker=pingan`, `methods=[buy_submit_once, confirm_current]`, and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
