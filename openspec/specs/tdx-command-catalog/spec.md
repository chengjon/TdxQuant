# tdx-command-catalog Specification

## Purpose
定义统一 command catalog 顶层入口，把跨 `task` / `report` / `trade` 的高频 preset 收敛为单一日常命令目录层，同时保持现有 preset workflow 的执行路径不变。
## Requirements
### Requirement: Command catalog CLI SHALL expose a unified daily entry registry
The system SHALL provide a top-level command catalog that lists stable daily entries mapped to existing `task`, `report`, or `trade` preset workflows.

#### Scenario: Caller requests a summary view for a catalog list
- **WHEN** a caller executes a catalog listing command with summary output enabled
- **THEN** the system MUST return a reduced discovery-oriented summary view instead of the full detailed list payload

#### Scenario: Caller receives stable catalog list ordering
- **WHEN** a caller executes the catalog listing command repeatedly with the same filter set
- **THEN** the system MUST return entries and bundles in a stable deterministic order

### Requirement: Command catalog CLI SHALL execute named entries through existing preset workflows
The system SHALL allow callers to execute a named catalog entry that resolves to exactly one supported preset in the `task`, `report`, or `trade` command groups.

#### Scenario: Caller requests a summary view for a catalog execution
- **WHEN** a caller executes a catalog run command with summary output enabled
- **THEN** the system MUST return a reduced summary view of the resolved execution result instead of the full detailed result payload

### Requirement: Command catalog CLI SHALL support named multi-step bundles composed from existing catalog entries
The system SHALL allow callers to define a named bundle that references multiple existing catalog entries and executes them sequentially through the existing single-entry dispatch path.

#### Scenario: Caller lists available catalog bundles
- **WHEN** a caller executes the catalog listing command for bundles
- **THEN** the system MUST return the available bundle names together with their resolved step metadata

#### Scenario: Caller filters catalog bundles by label
- **WHEN** a caller executes the catalog listing command for bundles with a label filter
- **THEN** the system MUST return only bundles whose configured labels include that label

### Requirement: Command catalog SHALL expose audit-oriented report entries and a diagnostic bundle once trade audit reports are stable
The system SHALL expose stable catalog entries for the existing trade audit report presets and allow at least one named bundle to combine audit review with an existing diagnostic entry.

#### Scenario: Caller lists audit-oriented catalog entries
- **WHEN** a caller lists catalog entries after stable trade audit report presets are available
- **THEN** the catalog MUST include audit-oriented report entries mapped to those presets

#### Scenario: Caller lists an audit diagnostic bundle
- **WHEN** a caller lists catalog bundles after stable trade audit report presets are available
- **THEN** the catalog MUST include at least one audit-oriented bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose split-step desktop trade task entries and a confirm follow-up bundle once the workflows are stable
The system SHALL expose stable catalog entries for the existing split-step desktop trade task presets and allow at least one named bundle to combine confirmation with an existing audit review entry.

#### Scenario: Caller lists split-step catalog entries
- **WHEN** a caller lists catalog entries after stable split-step desktop trade task presets are available
- **THEN** the catalog MUST include split-step task entries mapped to those presets

#### Scenario: Caller lists a confirm follow-up bundle
- **WHEN** a caller lists catalog bundles after stable split-step desktop trade task presets are available
- **THEN** the catalog MUST include at least one confirm-oriented bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose richer audit diagnostics and confirm follow-up bundles once trade audit and split-step workflows are stable
The system SHALL expose stable catalog entries for rejected-oriented audit presets and allow named bundles that combine those diagnostics or combine current confirmation with existing report follow-up entries.

#### Scenario: Caller lists rejected audit catalog entries
- **WHEN** a caller lists catalog entries after rejected-oriented trade audit presets are available
- **THEN** the catalog MUST include entries mapped to those rejected-oriented presets

#### Scenario: Caller lists richer audit and confirm follow-up bundles
- **WHEN** a caller lists catalog bundles after stable rejected audit presets and split-step confirm workflows are available
- **THEN** the catalog MUST include at least one rejection-diagnostic bundle and at least one confirm follow-up bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose richer trade-audit status entries and review bundles once those status presets are stable
The system SHALL expose stable catalog entries for the richer confirmed/replayed trade-audit presets and allow at least one named confirmed-review bundle and at least one replay-review bundle composed from existing catalog entries.

#### Scenario: Caller lists richer trade-audit status catalog entries
- **WHEN** a caller lists catalog entries after richer trade-audit status presets are available
- **THEN** the catalog MUST include entries mapped to those richer status presets

#### Scenario: Caller lists richer trade-audit status review bundles
- **WHEN** a caller lists catalog bundles after richer trade-audit status presets are available
- **THEN** the catalog MUST include at least one confirmed-review bundle and at least one replay-review bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose failed-oriented trade-audit entries and a failure diagnostics bundle once those presets are stable
The system SHALL expose stable catalog entries for the failed-oriented trade-audit presets and allow at least one named bundle to combine failed audit review with an existing failure-oriented entry.

#### Scenario: Caller lists failed-oriented trade-audit catalog entries
- **WHEN** a caller lists catalog entries after failed-oriented trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to those failed-oriented presets

#### Scenario: Caller lists a failed-oriented diagnostics bundle
- **WHEN** a caller lists catalog bundles after failed-oriented trade-audit presets are available
- **THEN** the catalog MUST include at least one failed-oriented diagnostics bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose exception-oriented trade-audit presets and a diagnostics bundle once multi-status filtering is stable
The system SHALL expose stable preset-backed catalog entries for exception-oriented trade-audit review and allow at least one named diagnostics bundle to combine that review with an existing failure-oriented entry.

#### Scenario: Caller lists exception-oriented trade-audit entries
- **WHEN** a caller lists catalog entries after multi-status trade-audit filtering is available
- **THEN** the catalog MUST include entries backed by stable exception-oriented trade-audit presets

#### Scenario: Caller lists an exception diagnostics bundle
- **WHEN** a caller lists catalog bundles after multi-status trade-audit filtering is available
- **THEN** the catalog MUST include at least one exception-oriented diagnostics bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose confirm-oriented exception audit entries and bundles once multidimensional presets and split-step confirm workflows are stable
The system SHALL expose stable catalog entries mapped to confirm-oriented exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine current confirmation with the new confirm-oriented exception review.

#### Scenario: Caller lists confirm-oriented exception catalog entries
- **WHEN** a caller lists catalog entries after confirm-oriented exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-confirm-exceptions` and `audit-period-confirm-exceptions`

#### Scenario: Caller lists confirm-oriented diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after confirm-oriented exception presets and split-step confirm workflows are stable
- **THEN** the catalog MUST include at least one confirm-oriented diagnostics bundle and at least one confirm-oriented follow-up bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose submit-once-oriented exception audit entries and bundles once multidimensional presets and full-submit workflows are stable
The system SHALL expose stable catalog entries mapped to submit-once-oriented exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine full-submit follow-up with the new submit-once exception review.

#### Scenario: Caller lists submit-once-oriented exception catalog entries
- **WHEN** a caller lists catalog entries after submit-once-oriented exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-submit-once-exceptions` and `audit-period-submit-once-exceptions`

#### Scenario: Caller lists submit-once-oriented diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after submit-once-oriented exception presets and full-submit workflows are stable
- **THEN** the catalog MUST include at least one submit-once-oriented diagnostics bundle and at least one submit-once-oriented follow-up bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose buy-oriented exception audit entries and bundles once multidimensional presets and guarded-buy workflows are stable
The system SHALL expose stable catalog entries mapped to buy-oriented exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine guarded-buy follow-up with the new buy exception review.

#### Scenario: Caller lists buy-oriented exception catalog entries
- **WHEN** a caller lists catalog entries after buy-oriented exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-buy-exceptions` and `audit-period-buy-exceptions`

#### Scenario: Caller lists buy-oriented diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after buy-oriented exception presets and guarded-buy workflows are stable
- **THEN** the catalog MUST include at least one buy-oriented diagnostics bundle and at least one buy-oriented follow-up bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose submit-path exception entries and bundles once multi-method presets are stable
The system SHALL expose stable catalog entries mapped to submit-path exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine current confirmation with the new submit-path exception review.

#### Scenario: Caller lists submit-path exception catalog entries
- **WHEN** a caller lists catalog entries after submit-path exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-submit-path-exceptions` and `audit-period-submit-path-exceptions`

#### Scenario: Caller lists submit-path diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after submit-path exception presets and stable confirm workflows are available
- **THEN** the catalog MUST include at least one submit-path diagnostics bundle and at least one submit-path follow-up bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose broker-scoped submit-path exception entries and bundles once broker-scoped presets are stable
The system SHALL expose stable catalog entries mapped to broker-scoped submit-path exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine current confirmation with the new broker-scoped submit-path exception review.

#### Scenario: Caller lists broker-scoped submit-path exception catalog entries
- **WHEN** a caller lists catalog entries after broker-scoped submit-path exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-pingan-submit-path-exceptions` and `audit-period-pingan-submit-path-exceptions`

#### Scenario: Caller lists broker-scoped submit-path diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after broker-scoped submit-path exception presets and stable confirm workflows are available
- **THEN** the catalog MUST include at least one broker-scoped submit-path diagnostics bundle and at least one broker-scoped submit-path follow-up bundle composed from existing catalog entries

### Requirement: Command catalog SHALL expose block watchlist export task entries once the preset is stable
The system SHALL expose stable catalog entries for preset-backed block watchlist export task workflows once those presets are available.

#### Scenario: Caller lists block watchlist export catalog entries
- **WHEN** a caller lists catalog entries after the stable `export-zxg-watchlist` task preset is available
- **THEN** the catalog MUST include a task-source entry mapped to that preset

#### Scenario: Caller plans a block watchlist export catalog entry
- **WHEN** a caller executes `catalog plan --entry export-zxg-watchlist`
- **THEN** the system MUST resolve the existing preset-backed task namespace without executing the task workflow

#### Scenario: Caller runs a block watchlist export catalog entry
- **WHEN** a caller executes `catalog run --entry export-zxg-watchlist`
- **THEN** the system MUST dispatch through the existing task-preset workflow instead of inventing a second execution path

### Requirement: Command catalog SHALL expose block read watchlist task entries once the preset is stable
The system SHALL expose stable catalog entries for preset-backed block read watchlist snapshot task workflows once those presets are available.

#### Scenario: Caller lists block read watchlist catalog entries
- **WHEN** a caller lists catalog entries after the stable `read-zxg-watchlist` task preset is available
- **THEN** the catalog MUST include a task-source entry mapped to that preset

#### Scenario: Caller plans a block read watchlist catalog entry
- **WHEN** a caller executes `catalog plan --entry read-zxg-watchlist`
- **THEN** the system MUST resolve the existing preset-backed task namespace without executing the task workflow

#### Scenario: Caller runs a block read watchlist catalog entry
- **WHEN** a caller executes `catalog run --entry read-zxg-watchlist`
- **THEN** the system MUST dispatch through the existing task-preset workflow instead of inventing a second execution path

### Requirement: Command catalog SHALL expose block read watchlist review bundles once the preset-backed entries are stable
The system SHALL expose stable catalog bundles that compose preset-backed block read watchlist snapshot and diagnostics entries through the existing bundle workflow.

#### Scenario: Caller lists block read watchlist review bundles
- **WHEN** a caller lists catalog bundles after the stable `read-zxg-watchlist` and `read-zxg-full` task presets are available
- **THEN** the catalog MUST include a bundle named `read-zxg-review`

#### Scenario: Caller plans a block read watchlist review bundle
- **WHEN** a caller executes `catalog plan --bundle read-zxg-review`
- **THEN** the system MUST resolve exactly two steps through the existing preset-backed entry workflow without executing the steps

#### Scenario: Caller applies a top-level block code override to the review bundle
- **WHEN** a caller executes `catalog plan` or `catalog run` for `read-zxg-review` with `--block-code <value>`
- **THEN** the system MUST propagate that `block_code` override to `read-zxg-watchlist` and `read-zxg-full`

#### Scenario: Caller runs a block read watchlist review bundle
- **WHEN** a caller executes `catalog run --bundle read-zxg-review`
- **THEN** the system MUST dispatch the two resolved steps sequentially through the existing bundle workflow and stop before `read-zxg-full` if `read-zxg-watchlist` fails

### Requirement: Command catalog SHALL expose block read review-and-export bundles once the preset-backed entries are stable
The system SHALL expose stable catalog bundles that compose preset-backed block read watchlist snapshot, diagnostics, and JSON export entries through the existing bundle workflow.

#### Scenario: Caller lists block read review-and-export bundles
- **WHEN** a caller lists catalog bundles after the stable `read-zxg-watchlist`, `read-zxg-full`, and `export-zxg-watchlist` task presets are available
- **THEN** the catalog MUST include a bundle named `read-zxg-review-and-export`

#### Scenario: Caller plans a block read review-and-export bundle
- **WHEN** a caller executes `catalog plan --bundle read-zxg-review-and-export`
- **THEN** the system MUST resolve exactly three steps through the existing preset-backed entry workflow without executing the steps

#### Scenario: Caller applies a top-level block code override to the review-and-export bundle
- **WHEN** a caller executes `catalog plan` or `catalog run` for `read-zxg-review-and-export` with `--block-code <value>`
- **THEN** the system MUST propagate that `block_code` override to `read-zxg-watchlist`, `read-zxg-full`, and `export-zxg-watchlist`

#### Scenario: Caller runs a block read review-and-export bundle
- **WHEN** a caller executes `catalog run --bundle read-zxg-review-and-export`
- **THEN** the system MUST dispatch all resolved steps sequentially through the existing bundle workflow and stop before the export step if `read-zxg-full` fails

### Requirement: Command catalog SHALL expose block read full task entries once the preset is stable
The system SHALL expose stable catalog entries for preset-backed block read full diagnostics task workflows once those presets are available.

#### Scenario: Caller lists block read full catalog entries
- **WHEN** a caller lists catalog entries after the stable `read-zxg-full` task preset is available
- **THEN** the catalog MUST include a task-source entry mapped to that preset

#### Scenario: Caller plans a block read full catalog entry
- **WHEN** a caller executes `catalog plan --entry read-zxg-full`
- **THEN** the system MUST resolve the existing preset-backed task namespace without executing the task workflow

#### Scenario: Caller runs a block read full catalog entry
- **WHEN** a caller executes `catalog run --entry read-zxg-full`
- **THEN** the system MUST dispatch through the existing task-preset workflow instead of inventing a second execution path

### Requirement: Command catalog CLI SHALL expose discovery metadata for list output
The catalog list workflow SHALL return deterministic discovery metadata for entries and bundles without changing the underlying catalog JSON schema.

#### Scenario: Caller lists catalog entries with a label filter
- **WHEN** a caller executes `catalog list --kind entry --label <value>`
- **THEN** the result summary includes the selected label, matched entry count, and available entry labels
- **AND** every returned entry includes the selected label in its labels

#### Scenario: Caller lists catalog bundles with a label filter
- **WHEN** a caller executes `catalog list --kind bundle --label <value>`
- **THEN** the result summary includes the selected label, matched bundle count, and available bundle labels
- **AND** every returned bundle includes the selected label in its labels

### Requirement: Command catalog CLI SHALL support non-executing preview output
The catalog CLI SHALL expose a `preview` command that resolves the same entry or bundle target as `plan`, returns stable preview metadata, and does not execute the underlying preset workflow.

#### Scenario: Caller previews a catalog entry
- **WHEN** a caller executes `catalog preview --entry <name>`
- **THEN** the result reports `mode` as `preview`
- **AND** includes the resolved dispatch command and selected key arguments
- **AND** does not execute the underlying task, report, or trade workflow

#### Scenario: Caller previews a catalog bundle range
- **WHEN** a caller executes `catalog preview --bundle <name>` with optional step range arguments
- **THEN** the result reports `mode` as `preview`
- **AND** includes selected bundle range metadata and preview steps in deterministic order

### Requirement: Command catalog CLI SHALL constrain summary-view payloads
The catalog summary view SHALL expose stable reduced fields for list, plan, preview, and run results so callers do not depend on full detailed payload internals.

#### Scenario: Caller requests summary view for catalog preview
- **WHEN** a caller executes `catalog preview` with `--view summary`
- **THEN** the selected output payload includes only summary metadata, target metadata, dispatch or step summaries, and selected key arguments

### Requirement: Command catalog SHALL expose tested task/report combo bundles for daily follow-up workflows

The system SHALL expose stable named catalog bundles that compose at least one task-source entry with one or more report-source entries for daily follow-up workflows, while preserving the existing bundle planning and dispatch model.

#### Scenario: Caller discovers task/report combo bundles by label

- **WHEN** a caller lists catalog bundles with a follow-up label filter
- **THEN** the catalog MUST include at least one bundle composed from both task-source and report-source entries

#### Scenario: Caller plans a task/report combo bundle without execution

- **WHEN** a caller plans a task/report combo bundle such as `confirm-complete-review`
- **THEN** the plan MUST include the resolved task step and report steps without dispatching execution
- **AND** the selected-step metadata MUST identify the full bundle step count

#### Scenario: Task/report combo bundles preserve existing execution boundaries

- **WHEN** a task/report combo bundle is listed or planned
- **THEN** the system MUST treat it as a composition of existing catalog entries rather than a new task, report, or trading capability contract

### Requirement: Command catalog SHALL expose a plan-able block watchlist import entry

The command catalog SHALL expose a task-source entry for the JSON watchlist import wrapper so callers can discover and plan the import path without executing provider mutations.

#### Scenario: Caller lists block import catalog entries

- **WHEN** a caller lists catalog entries with the `block` or `import` label
- **THEN** the catalog MUST include a task-source entry for block watchlist import

#### Scenario: Caller plans a block import catalog entry

- **WHEN** a caller executes `catalog plan --entry <block-import-entry>`
- **THEN** the plan MUST resolve to the task command and include the preset-owned import path without dispatching execution
