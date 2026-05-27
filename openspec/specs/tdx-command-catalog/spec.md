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

### Requirement: Command catalog SHALL expose a plan-able block sync write-policy entry

The command catalog SHALL expose a task-source entry for the safe block sync write-policy preset so callers can discover and plan the workflow without implying that provider mutation is automatic.

#### Scenario: Caller lists block sync catalog entries

- **WHEN** a caller lists catalog entries with the `block`, `sync`, or `dry-run` label
- **THEN** the catalog MUST include a task-source entry for the block sync write-policy plan

#### Scenario: Caller plans a block sync catalog entry

- **WHEN** a caller executes `catalog plan --entry plan-zxg-block-sync-merge`
- **THEN** the plan MUST resolve to the task command and include the explicit dry-run write policy without dispatching execution

### Requirement: Command catalog plan and preview SHALL expose non-execution provenance
The command catalog `plan` and `preview` workflows SHALL include machine-readable provenance and non-execution constraint metadata for entry and bundle targets without mutating runtime catalog schemas or changing `catalog run` execution semantics.

#### Scenario: Caller plans a catalog entry with provenance
- **WHEN** a caller executes `catalog plan --entry <name>`
- **THEN** the result includes provenance metadata with `mode`, `target_type`, `target_name`, and `catalog_path`
- **AND** the result includes constraints stating that execution mode is non-executing and dispatch was not executed
- **AND** the underlying catalog entry dispatch workflow is not invoked

#### Scenario: Caller previews a catalog bundle summary with provenance
- **WHEN** a caller executes `catalog preview --bundle <name>` with `--view summary`
- **THEN** the selected output payload includes provenance metadata with `mode`, `target_type`, `target_name`, `catalog_path`, and `bundle_path`
- **AND** the selected output payload includes constraints stating that dispatch was not executed, schema files were not mutated, and run semantics were not changed
- **AND** the underlying bundle dispatch workflow is not invoked

#### Scenario: Catalog run behavior is unchanged
- **WHEN** a caller executes `catalog run` for an entry or bundle
- **THEN** the existing run dispatch semantics remain unchanged
- **AND** the provenance and constraint metadata added for non-executing plan/preview workflows does not change runtime catalog or bundle JSON schemas

### Requirement: Command catalog SHALL expose the desktop broker capability probe as a non-executing entry
The command catalog SHALL include a stable entry for the PingAn desktop extended broker capability probe so callers can discover and plan the diagnostic boundary without executing live broker actions.

#### Scenario: Caller lists broker capability catalog entries
- **WHEN** a caller lists catalog entries with the `broker` or `capability` label
- **THEN** the catalog includes a trade-source entry for the broker capability probe
- **AND** the entry resolves to the stable broker capability trade preset

#### Scenario: Caller plans the broker capability catalog entry
- **WHEN** a caller executes `catalog plan --entry broker-capabilities`
- **THEN** the plan resolves to the trade `broker-capabilities` command
- **AND** the plan includes non-execution provenance and constraints
- **AND** the underlying broker capability probe is not executed

### Requirement: Command catalog SHALL expose Ping An sell submit-once audit diagnostics

The command catalog SHALL expose Ping An `sell_submit_once` report entries and bundles without requiring a separate roadmap document.

#### Scenario: Caller lists Ping An sell submit-once audit catalog entries

- **WHEN** a caller filters command catalog entries by `sell-submit-once`
- **THEN** the catalog MUST include daily and period Ping An `sell_submit_once` exception, rejected, and failed report entries

#### Scenario: Caller plans Ping An sell submit-once follow-up bundle

- **WHEN** a caller plans a Ping An sell submit-once follow-up bundle
- **THEN** the plan MUST include a `task-submit-once` step with `side=sell`
- **AND** the plan MUST include the matching Ping An `sell_submit_once` audit report entry

### Requirement: Command catalog SHALL expose ordinary Ping An sell task follow-up bundles

The command catalog SHALL expose the existing ordinary sell task workflow and fixed Ping An sell audit follow-up bundles without adding new sell execution semantics.

#### Scenario: Caller lists the task sell catalog entry

- **WHEN** a caller filters command catalog entries by `sell`
- **THEN** the catalog MUST include `task-sell`
- **AND** the entry MUST resolve to the `task-sell-default` task preset

#### Scenario: Caller plans an ordinary Ping An sell follow-up bundle with explicit order inputs

- **WHEN** a caller plans an ordinary Ping An sell follow-up bundle with explicit `code`, `price`, and `quantity`
- **THEN** the plan MUST include a task step resolving to `trade-sell`
- **AND** the plan MUST include the matching existing Ping An sell audit report preset
- **AND** planning MUST remain non-executing

### Requirement: Command catalog SHALL expose a side-explicit sell submit-once task entry

The command catalog SHALL expose a side-explicit sell submit-once task entry and use it for Ping An sell submit-once follow-up bundles.

#### Scenario: Caller lists the sell submit-once task catalog entry

- **WHEN** a caller filters command catalog entries by `sell-submit-once`
- **THEN** the catalog MUST include `task-sell-submit-once`
- **AND** the entry MUST resolve to the `sell-submit-once-default` task preset

#### Scenario: Caller plans a Ping An sell submit-once follow-up bundle

- **WHEN** a caller plans a Ping An sell submit-once follow-up bundle with explicit `code`, `price`, and `quantity`
- **THEN** the plan MUST include a task step whose entry is `task-sell-submit-once`
- **AND** the task step MUST resolve to `trade-submit-once` with `side=sell`
- **AND** the plan MUST include the matching existing Ping An sell submit-once audit report preset
- **AND** planning MUST remain non-executing

### Requirement: Command catalog SHALL expose method-explicit Ping An confirm_current follow-up bundles
The system SHALL expose stable command bundle aliases for Ping An confirm_current follow-up review that compose the existing confirm task entry with existing Ping An confirm audit report entries.

#### Scenario: Caller lists method-explicit Ping An confirm_current bundles
- **WHEN** a caller filters catalog bundles by `confirm-current`
- **THEN** the catalog MUST include `confirm-current-pingan-exception-review`
- **AND** the catalog MUST include `confirm-current-pingan-rejection-review`
- **AND** the catalog MUST include `confirm-current-pingan-failure-review`

#### Scenario: Caller plans a method-explicit Ping An confirm_current exception bundle
- **WHEN** a caller plans `confirm-current-pingan-exception-review`
- **THEN** the plan MUST include a task step whose entry is `task-confirm-current`
- **AND** the plan MUST include the matching existing Ping An confirm exception audit report entry
- **AND** planning MUST remain non-executing

### Requirement: Command catalog SHALL expose explicit buy submit-once task entry and follow-up bundles
The command catalog SHALL expose a side-explicit buy submit-once task entry and buy-scoped PingAn follow-up bundles while continuing to route execution through existing `trade-submit-once` task behavior.

#### Scenario: Caller lists buy submit-once task entry
- **WHEN** a caller lists catalog entries with a `buy-submit-once` label
- **THEN** the catalog MUST include `task-buy-submit-once`
- **AND** the entry MUST resolve to a task preset whose command is `trade-submit-once` and whose options include `side=buy`

#### Scenario: Caller plans buy submit-once PingAn follow-up bundle
- **WHEN** a caller plans `buy-submit-once-pingan-exception-review`
- **THEN** the bundle MUST resolve a trade step through `task-buy-submit-once`
- **AND** the audit step MUST resolve through an existing PingAn buy submit-once audit report entry
- **AND** planning MUST NOT execute the trade or report steps

#### Scenario: Existing default submit-once entries remain available
- **WHEN** the explicit buy entry is registered
- **THEN** existing `submit-once` and `task-submit-once` catalog entries MUST remain present
- **AND** existing `task-sell-submit-once` behavior MUST remain side-scoped to sell

### Requirement: Command catalog SHALL expose a buy submit-once PingAn complete-review bundle
The command catalog SHALL expose a buy-scoped PingAn submit-once complete-review bundle that composes existing task and report entries without changing the underlying trade execution path.

#### Scenario: Caller plans buy submit-once PingAn complete review
- **WHEN** a caller plans `buy-submit-once-pingan-complete-review`
- **THEN** the bundle MUST resolve its trade step through `task-buy-submit-once`
- **AND** the bundle MUST include existing success and PingAn confirmed audit report entries
- **AND** planning MUST NOT execute the trade or report steps

#### Scenario: Existing generic submit-once complete review remains available
- **WHEN** the buy-scoped bundle is registered
- **THEN** existing `submit-once-pingan-complete-review` MUST remain available
- **AND** the new bundle MUST NOT replace or remove generic submit-once catalog behavior

### Requirement: Command catalog SHALL expose a confirm-current PingAn complete-review alias
The command catalog SHALL expose a `confirm-current-pingan-complete-review` bundle that composes existing confirm-current task and report entries without changing the underlying desktop execution path.

#### Scenario: Caller plans confirm-current PingAn complete review
- **WHEN** a caller plans `confirm-current-pingan-complete-review`
- **THEN** the bundle MUST resolve its confirm step through `task-confirm-current`
- **AND** the bundle MUST include existing success and PingAn confirmed audit report entries
- **AND** planning MUST NOT execute the task or report steps

#### Scenario: Existing confirm PingAn complete review remains available
- **WHEN** the confirm-current alias is registered
- **THEN** existing `confirm-pingan-complete-review` MUST remain available
- **AND** the new alias MUST NOT replace or remove existing confirm catalog behavior

### Requirement: Command catalog SHALL expose an ordinary buy PingAn complete-review bundle
The command catalog SHALL expose a `buy-pingan-complete-review` bundle that composes the existing ordinary buy task entry with success and PingAn confirmed audit report entries.

#### Scenario: Caller plans ordinary buy PingAn complete review
- **WHEN** a caller plans `buy-pingan-complete-review`
- **THEN** the bundle MUST resolve its trade step through `task-buy`
- **AND** the bundle MUST include existing success and PingAn confirmed audit report entries
- **AND** planning MUST NOT execute the task or report steps

#### Scenario: Existing guarded-buy PingAn complete review remains available
- **WHEN** the ordinary buy bundle is registered
- **THEN** existing `guarded-pingan-buy-complete-review` MUST remain available
- **AND** the new bundle MUST NOT replace or remove guarded-buy catalog behavior

### Requirement: Command catalog SHALL expose ordinary buy PingAn exception bundles
The command catalog SHALL expose ordinary buy PingAn exception, rejection, and failure bundles that compose existing task and report entries without changing the underlying execution path.

#### Scenario: Caller plans ordinary buy PingAn exception review
- **WHEN** a caller plans `buy-pingan-exception-review`
- **THEN** the bundle MUST resolve its trade step through `task-buy`
- **AND** the bundle MUST resolve its audit step through `audit-daily-pingan-buy-exceptions`
- **AND** planning MUST NOT execute the task or report steps

#### Scenario: Caller plans ordinary buy PingAn rejection review
- **WHEN** a caller plans `buy-pingan-rejection-review`
- **THEN** the bundle MUST resolve its trade step through `task-buy`
- **AND** the bundle MUST resolve its audit step through `audit-daily-pingan-buy-rejected`

#### Scenario: Caller plans ordinary buy PingAn failure review
- **WHEN** a caller plans `buy-pingan-failure-review`
- **THEN** the bundle MUST resolve its trade step through `task-buy`
- **AND** the bundle MUST resolve its audit step through `audit-daily-pingan-buy-failed`

#### Scenario: Existing guarded-buy bundles remain available
- **WHEN** the ordinary buy bundles are registered
- **THEN** existing guarded-buy PingAn bundles MUST remain available
- **AND** the new bundles MUST NOT replace or remove guarded-buy catalog behavior

### Requirement: Command catalog SHALL expose ordinary sell PingAn complete-review bundle
The command catalog SHALL expose an ordinary sell PingAn complete-review bundle that composes existing task and report entries without changing the underlying execution path.

#### Scenario: Caller plans ordinary sell PingAn complete review
- **WHEN** a caller plans `sell-pingan-complete-review`
- **THEN** the bundle MUST resolve its trade step through `task-sell`
- **AND** the bundle MUST resolve its success report step through `daily-success`
- **AND** the bundle MUST resolve its audit step through `audit-daily-pingan-confirmed`
- **AND** planning MUST NOT execute the task or report steps

#### Scenario: Existing ordinary sell PingAn exception bundles remain available
- **WHEN** the complete-review bundle is registered
- **THEN** existing ordinary sell PingAn exception, rejection, and failure bundles MUST remain available
- **AND** the new bundle MUST NOT replace or remove existing sell PingAn catalog behavior

### Requirement: Command catalog SHALL expose sell submit-once PingAn complete-review bundle
The command catalog SHALL expose a sell submit-once PingAn complete-review bundle that composes existing task and report entries without changing the underlying execution path.

#### Scenario: Caller plans sell submit-once PingAn complete review
- **WHEN** a caller plans `sell-submit-once-pingan-complete-review`
- **THEN** the bundle MUST resolve its trade step through `task-sell-submit-once`
- **AND** the trade step MUST preserve `side=sell`
- **AND** the bundle MUST resolve its success report step through `daily-success`
- **AND** the bundle MUST resolve its audit step through `audit-daily-pingan-confirmed`
- **AND** planning MUST NOT execute the task or report steps

#### Scenario: Existing sell submit-once PingAn exception bundles remain available
- **WHEN** the complete-review bundle is registered
- **THEN** existing sell submit-once PingAn exception, rejection, and failure bundles MUST remain available
- **AND** the new bundle MUST NOT replace or remove existing sell submit-once PingAn catalog behavior

### Requirement: Command catalog SHALL validate fixed registry entries without execution

The command catalog CLI SHALL provide a non-execution validation path that checks
selected catalog entries and bundles resolve through the existing registry
metadata and reports task/report bundle coverage.

#### Scenario: Caller validates the full catalog registry

- **WHEN** a caller runs `catalog validate --kind all`
- **THEN** the system MUST resolve all selected catalog entries and bundles without executing any task, report, trade, or bundle step
- **AND** the result MUST include entry count, bundle count, task/report bundle count, invalid count, and validation status

#### Scenario: Caller validates follow-up bundles by label

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the system MUST validate only selected bundles with that label
- **AND** the task/report bundle count MUST reflect bundles whose resolved steps include both task and report sources
- **AND** the result MUST include the bounded sample limit used for `task_report_bundle_samples`
- **AND** the result MUST indicate whether `task_report_bundle_samples` was truncated

#### Scenario: Caller validates an unsupported target

- **WHEN** a caller runs `catalog validate` for a missing entry or bundle
- **THEN** the system MUST return an invalid-request result with a structured error
- **AND** it MUST NOT execute any selected catalog target

### Requirement: Command catalog validate SHALL expose opt-in summary view

The command catalog validation workflow SHALL expose an opt-in summary view that projects validation counts and non-execution status without changing the default detailed validation payload.

#### Scenario: Caller validates follow-up bundles with summary view

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include validation mode, selected kind, selected label, bundle count, invalid count, and valid flag
- **AND** the summary payload MUST include `task_report_bundle_count`
- **AND** the summary payload MUST include a bounded deterministic `task_report_bundle_samples` list when matching task+report bundles exist
- **AND** the summary payload MUST include `task_report_bundle_sample_limit`
- **AND** the summary payload MUST include `task_report_bundle_sample_truncated`
- **AND** the summary payload MUST declare `non_execution=true`
- **AND** the summary payload MUST NOT include full entry or bundle detail rows

#### Scenario: Caller validates submit-once bundles with summary view

- **WHEN** a caller runs `catalog validate --kind bundle --label submit-once --view summary`
- **THEN** the summary payload MUST include `submit_once_bundle_count`
- **AND** the summary payload MUST include a bounded deterministic `submit_once_bundle_samples` list when matching submit-once bundles exist
- **AND** the summary payload MUST include `submit_once_bundle_sample_limit`
- **AND** the summary payload MUST include `submit_once_bundle_sample_truncated`
- **AND** the summary payload MUST declare `non_execution=true`
- **AND** the summary payload MUST NOT include full entry or bundle detail rows

#### Scenario: Caller validates PingAn bundles with summary view

- **WHEN** a caller runs `catalog validate --kind bundle --label pingan --view summary`
- **THEN** the summary payload MUST include `pingan_bundle_count`
- **AND** the summary payload MUST include a bounded deterministic `pingan_bundle_samples` list when matching PingAn bundles exist
- **AND** the summary payload MUST include `pingan_bundle_sample_limit`
- **AND** the summary payload MUST include `pingan_bundle_sample_truncated`
- **AND** the summary payload MUST declare `non_execution=true`
- **AND** the summary payload MUST NOT include full entry or bundle detail rows

#### Scenario: Caller validates missing target with summary view

- **WHEN** a caller runs `catalog validate --bundle <missing> --view summary`
- **THEN** the summary payload MUST preserve the invalid request code and validation error details
- **AND** the summary payload MUST still declare `non_execution=true`

#### Scenario: Caller omits validate summary view

- **WHEN** a caller runs `catalog validate` without `--view summary`
- **THEN** the detailed validation payload MUST remain the default printed result

### Requirement: Command catalog plan summary SHALL expose selected step source counts

The command catalog SHALL include a compact `step_source_counts` object in bundle `plan` and `preview` summary views, derived from the selected resolved steps without executing catalog dispatch.

#### Scenario: Caller plans a mixed task/report bundle summary

- **WHEN** a caller executes `catalog plan --bundle <task-report-bundle> --view summary`
- **THEN** the summary view MUST include `step_source_counts` with counts for the selected task and report steps
- **AND** the summary view MUST continue to include non-execution provenance and constraints
- **AND** the underlying catalog step dispatch workflow MUST NOT be invoked

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --only-step <step> --view summary`
- **THEN** `step_source_counts` MUST reflect only the selected step range
- **AND** the summary view MUST continue to report the selected step count

### Requirement: Command catalog trade plan summary SHALL expose non-execution trade input boundaries

The command catalog SHALL include a `trade_plan_boundary` in plan/preview summary views for trade-related catalog entries and selected bundle steps, derived from resolved dispatch metadata and arguments without executing catalog dispatch.

#### Scenario: Caller plans a trade entry with summary view

- **WHEN** a caller executes `catalog plan --entry <trade-entry> --view summary`
- **THEN** the summary view MUST include `trade_plan_boundary`
- **AND** the boundary MUST include the resolved trade command, non-executing execution mode, dispatch-executed flag, required input fields, provided input fields, and missing input fields
- **AND** the plan MUST retain non-execution provenance and constraints
- **AND** the underlying trade/task dispatch workflow MUST NOT be invoked

#### Scenario: Caller plans a submit-once entry with summary view

- **WHEN** a caller executes `catalog plan --entry <submit-once-entry> --view summary`
- **THEN** `trade_plan_boundary` MUST include the resolved submit-once side when present
- **AND** it MUST report the submit-once input fields without executing trade dispatch

#### Scenario: Caller plans a trade follow-up bundle with summary view

- **WHEN** a caller executes `catalog plan --bundle <trade-follow-up-bundle> --view summary`
- **THEN** each selected trade-related step MUST include a `trade_plan_boundary`
- **AND** selected report-only steps MUST NOT be marked as trade plan boundaries
- **AND** the bundle plan MUST remain non-executing

### Requirement: Command catalog validate SHALL summarize task/report bundle step sources

The command catalog validation workflow SHALL expose compact aggregate source counts for selected task/report bundles, derived from resolved catalog metadata without executing catalog dispatch.

#### Scenario: Caller validates follow-up bundles with source counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_source_counts`
- **AND** the counts MUST aggregate resolved step sources only for bundles whose resolved steps include both `task` and `report`
- **AND** the counts MUST include task and report sources when matching task/report bundles exist
- **AND** the validation MUST NOT execute any selected task, report, trade, or bundle step

#### Scenario: Caller validates follow-up bundles with summary source counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_source_counts`
- **AND** the summary payload MUST retain `non_execution=true`
- **AND** the summary payload MUST NOT include full entry or bundle detail rows

### Requirement: Command catalog validate SHALL summarize task/report bundle labels

Catalog validation SHALL include an additive `task_report_bundle_label_counts` object derived from labels on resolved bundles that contain both task and report steps, without executing entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation exposes task/report label counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_label_counts`
- **AND** the counts MUST be derived only from resolved bundles containing both task and report steps
- **AND** the validation MUST remain non-executing

#### Scenario: Summary validation projects task/report label counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_label_counts`
- **AND** the summary value MUST match the detailed validation value
- **AND** the summary payload MUST continue to omit full entry and bundle definitions

#### Scenario: Missing or empty matches produce empty label counts

- **WHEN** no resolved task+report bundles match validation filters
- **THEN** `task_report_bundle_label_counts` MUST be an empty object
- **AND** the validation payload MUST still report existing validity and error fields

### Requirement: Command catalog trade plan boundary SHALL expose input coverage counts

Catalog plan and preview summary views SHALL include additive input coverage counts in `trade_plan_boundary` for trade-related catalog entries and selected bundle steps, derived from existing field lists without executing catalog dispatch.

#### Scenario: Trade entry summary includes input counts

- **WHEN** a caller executes `catalog plan --entry <trade-entry> --view summary`
- **THEN** `trade_plan_boundary.required_input_count` MUST equal the number of required input fields
- **AND** `trade_plan_boundary.provided_input_count` MUST equal the number of provided input fields
- **AND** `trade_plan_boundary.missing_input_count` MUST equal the number of missing input fields
- **AND** `trade_plan_boundary.dispatch_executed` MUST remain `false`

#### Scenario: Submit-once summary includes side and input counts

- **WHEN** a caller executes `catalog plan --entry <submit-once-entry> --view summary`
- **THEN** `trade_plan_boundary.side` MUST remain present when resolved
- **AND** input coverage counts MUST be derived from the submit-once boundary field lists
- **AND** the summary MUST remain non-executing

#### Scenario: Trade bundle step summary includes input counts

- **WHEN** a caller executes `catalog plan --bundle <trade-follow-up-bundle> --view summary`
- **THEN** each selected trade-related step with `trade_plan_boundary` MUST include input coverage counts
- **AND** non-trade steps MUST continue to omit `trade_plan_boundary`
- **AND** the bundle plan MUST remain non-executing

### Requirement: Command catalog trade plan boundary SHALL expose input coverage status

Catalog plan and preview summary views SHALL include an additive `trade_plan_boundary.input_coverage_status` field for trade-related catalog entries and selected bundle steps, derived only from existing required/provided/missing input fields and without executing catalog dispatch.

#### Scenario: Missing order inputs are explicit

- **WHEN** a caller executes `catalog plan --entry <trade-entry> --view summary` without all required order inputs
- **THEN** `trade_plan_boundary.input_coverage_status` MUST be `missing_required_inputs`
- **AND** `trade_plan_boundary.missing_input_count` MUST be greater than zero
- **AND** `trade_plan_boundary.dispatch_executed` MUST remain `false`

#### Scenario: Complete order inputs are explicit

- **WHEN** a caller executes `catalog plan --entry <trade-entry> --view summary` with all required order inputs resolved
- **THEN** `trade_plan_boundary.input_coverage_status` MUST be `complete`
- **AND** `trade_plan_boundary.missing_input_count` MUST be zero
- **AND** the summary MUST remain non-executing

#### Scenario: No-input confirmation commands are explicit

- **WHEN** a caller executes `catalog plan --entry <confirm-current-entry> --view summary`
- **THEN** `trade_plan_boundary.input_coverage_status` MUST be `no_required_inputs`
- **AND** required, provided, and missing input counts MUST all be zero
- **AND** the summary MUST remain non-executing

### Requirement: Command catalog validation SHALL expose task report bundle step count

Catalog validation SHALL include an additive `task_report_bundle_step_count` scalar derived from the number of resolved steps in bundles that contain both task and report steps, without executing entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation includes step count

- **WHEN** a caller runs catalog validation for bundles that contain both task and report steps
- **THEN** the validation payload MUST include `task_report_bundle_step_count`
- **AND** the count MUST equal the total resolved step count across matching task/report bundles
- **AND** validation MUST remain non-executing

#### Scenario: Summary validation includes step count

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_count`
- **AND** existing task/report bundle samples and aggregate counts MUST remain present

#### Scenario: No matching task report bundles has zero step count

- **WHEN** catalog validation selects no task/report bundles
- **THEN** `task_report_bundle_step_count` MUST be `0`
- **AND** task/report bundle source and label counts MUST remain empty objects

### Requirement: Command catalog validate SHALL expose bundle step count

The command catalog validation payload SHALL expose an additive read-only `bundle_step_count` scalar derived from the resolved bundle steps already processed by validation without executing catalog steps or changing dispatch behavior.

#### Scenario: Validation counts all resolved bundle steps

- **WHEN** a caller runs `catalog validate` against bundle rows
- **THEN** the validation payload MUST include `bundle_step_count`
- **AND** `bundle_step_count` MUST equal the total number of resolved steps across the selected bundles
- **AND** the validation payload MUST remain non-executing

#### Scenario: Summary view preserves bundle step count

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_step_count`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Catalog validate SHALL expose selected bundle label counts

`catalog validate` SHALL include an additive read-only `bundle_label_counts` object for selected bundle validation results, derived only from resolved bundle labels and without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Bundle validation reports selected label counts

- **WHEN** a caller validates selected bundles
- **THEN** the validation payload MUST include `bundle_label_counts`
- **AND** `bundle_label_counts` MUST count labels from the selected resolved bundles
- **AND** the validation payload MUST remain non-executing

#### Scenario: Summary view preserves selected label counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_label_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Catalog validate SHALL expose selected bundle step source counts

`catalog validate` SHALL include an additive read-only `bundle_step_source_counts` object for selected bundle validation results, derived only from resolved bundle steps and without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Bundle validation reports selected step source counts

- **WHEN** a caller validates selected bundles
- **THEN** the validation payload MUST include `bundle_step_source_counts`
- **AND** `bundle_step_source_counts` MUST count step sources from the selected resolved bundles
- **AND** the sum of `bundle_step_source_counts` values MUST equal `bundle_step_count`
- **AND** the validation payload MUST remain non-executing

#### Scenario: Summary view preserves selected step source counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Command catalog validate SHALL summarize selected bundle step names

`catalog validate` SHALL include an additive read-only `bundle_step_name_counts` object for selected bundle validation results, derived only from resolved bundle step names and without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation includes selected bundle step name counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_name_counts`
- **AND** `bundle_step_name_counts` MUST count step names from the selected resolved bundles
- **AND** the sum of `bundle_step_name_counts` values MUST equal `bundle_step_count`

#### Scenario: Summary view preserves selected bundle step name counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_step_name_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Command catalog validate SHALL summarize selected bundle step entries

`catalog validate` SHALL include an additive read-only `bundle_step_entry_counts` object for selected bundle validation results, derived only from resolved bundle step entries and without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation includes selected bundle step entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_entry_counts`
- **AND** `bundle_step_entry_counts` MUST count step entries from the selected resolved bundles
- **AND** the sum of `bundle_step_entry_counts` values MUST equal `bundle_step_count`

#### Scenario: Summary view preserves selected bundle step entry counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_step_entry_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Catalog validation SHALL expose selected bundle step source/name counts

`catalog validate` SHALL include additive `bundle_step_source_name_counts` for selected resolved bundle steps without executing task, report, trade, or bundle steps.

#### Scenario: Detailed validation counts selected bundle step source/name pairs

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_source_name_counts`
- **AND** keys MUST combine the selected step `source` and `name` as `source:name`
- **AND** the sum of `bundle_step_source_name_counts` values MUST equal `bundle_step_count`

#### Scenario: Summary view preserves selected bundle step source/name counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_name_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Catalog validation SHALL expose task/report bundle step-name counts

`catalog validate` SHALL include additive `task_report_bundle_step_name_counts` for selected resolved bundles that contain both task and report steps without executing task, report, trade, or bundle steps.

#### Scenario: Detailed validation counts task/report bundle step names

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_name_counts`
- **AND** the sum of `task_report_bundle_step_name_counts` values MUST equal `task_report_bundle_step_count`

#### Scenario: Summary view preserves task/report bundle step-name counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_name_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Catalog validation SHALL expose task/report bundle step source-name counts

`catalog validate` SHALL include additive `task_report_bundle_step_source_name_counts` for selected resolved bundles that contain both task and report steps without executing task, report, trade, or bundle steps.

#### Scenario: Detailed validation counts task/report bundle step source-name pairs

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_source_name_counts`
- **AND** the sum of `task_report_bundle_step_source_name_counts` values MUST equal `task_report_bundle_step_count`
- **AND** the count keys MUST combine step `source` and `name`

#### Scenario: Summary view preserves task/report bundle step source-name counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_source_name_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Catalog validation SHALL expose task/report bundle step entry counts

`catalog validate` SHALL include additive `task_report_bundle_step_entry_counts` for selected resolved bundles that contain both task and report steps without executing task, report, trade, or bundle steps.

#### Scenario: Detailed validation counts task/report bundle step entries

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_entry_counts`
- **AND** the sum of `task_report_bundle_step_entry_counts` values MUST equal `task_report_bundle_step_count`
- **AND** the count keys MUST be catalog step `entry` values

#### Scenario: Summary view preserves task/report bundle step entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_entry_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Catalog validate SHALL summarize selected bundle step option keys

`catalog validate` SHALL include additive read-only option-key count maps for selected resolved bundle steps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation counts selected bundle step option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_option_key_counts`
- **AND** `bundle_step_option_key_counts` MUST count option keys from selected resolved bundle steps whose `options` value is an object
- **AND** the validation payload MUST remain non-executing

#### Scenario: Detailed validation counts task/report bundle step option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_option_key_counts`
- **AND** the count map MUST be derived only from selected bundles that contain both task and report steps
- **AND** the validation payload MUST remain non-executing

#### Scenario: Summary view preserves selected bundle step option-key counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_option_key_counts`
- **AND** the summary payload MUST include `task_report_bundle_step_option_key_counts`
- **AND** both summary values MUST mirror the detailed validation values
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Catalog validate SHALL expose selected entry label counts

`catalog validate` SHALL include additive read-only `entry_label_counts` for selected resolved catalog entries without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation counts selected entry labels

- **WHEN** a caller validates selected entries
- **THEN** the validation payload MUST include `entry_label_counts`
- **AND** `entry_label_counts` MUST count labels from resolved entries that matched the validation filters
- **AND** the validation payload MUST remain non-executing

#### Scenario: Bundle-only validation has empty entry label counts

- **WHEN** a caller validates only bundles
- **THEN** `entry_label_counts` MUST be an empty object
- **AND** existing bundle validation counts MUST remain unchanged

#### Scenario: Summary view preserves selected entry label counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `entry_label_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Catalog validate SHALL expose selected entry source counts

`catalog validate` SHALL include additive read-only `entry_source_counts` for selected resolved catalog entries without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation counts selected entry sources

- **WHEN** a caller validates selected entries
- **THEN** the validation payload MUST include `entry_source_counts`
- **AND** `entry_source_counts` MUST count sources from resolved entries that matched the validation filters
- **AND** the validation payload MUST remain non-executing

#### Scenario: Bundle-only validation has empty entry source counts

- **WHEN** a caller validates only bundles
- **THEN** `entry_source_counts` MUST be an empty object
- **AND** existing bundle validation counts MUST remain unchanged

#### Scenario: Summary view preserves selected entry source counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `entry_source_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle label counts

`catalog validate` SHALL include additive `submit_once_bundle_label_counts` and `pingan_bundle_label_counts` objects derived from selected resolved bundle labels without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset label counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_label_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_label_counts`
- **AND** both fields MUST count labels from their matching resolved bundle subsets

#### Scenario: Summary view preserves subset label counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_label_counts`
- **AND** the summary view MUST include `pingan_bundle_label_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset label counts are registry metadata only

- **WHEN** submit-once or PingAn labels are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, or workflow-builder behavior

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle step-source counts

`catalog validate` SHALL include additive `submit_once_bundle_step_source_counts` and `pingan_bundle_step_source_counts` objects derived from selected resolved bundle step sources without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset step-source counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_step_source_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_step_source_counts`
- **AND** both fields MUST count resolved step sources from their matching bundle subsets

#### Scenario: Summary view preserves subset step-source counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_step_source_counts`
- **AND** the summary view MUST include `pingan_bundle_step_source_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset step-source counts are registry metadata only

- **WHEN** submit-once or PingAn resolved step sources are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, or workflow-builder behavior

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle step-name counts

`catalog validate` SHALL include additive `submit_once_bundle_step_name_counts` and `pingan_bundle_step_name_counts` objects derived from selected resolved bundle step names without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset step-name counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_step_name_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_step_name_counts`
- **AND** both fields MUST count resolved step names from their matching bundle subsets

#### Scenario: Summary view preserves subset step-name counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_step_name_counts`
- **AND** the summary view MUST include `pingan_bundle_step_name_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset step-name counts are registry metadata only

- **WHEN** submit-once or PingAn resolved step names are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, workflow-builder behavior, or complete execution-chain coverage

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle step source-name counts

`catalog validate` SHALL include additive `submit_once_bundle_step_source_name_counts` and `pingan_bundle_step_source_name_counts` objects derived from selected resolved bundle step `source:name` pairs without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset step source-name counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_step_source_name_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_step_source_name_counts`
- **AND** both fields MUST count resolved step `source:name` pairs from their matching bundle subsets

#### Scenario: Summary view preserves subset step source-name counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_step_source_name_counts`
- **AND** the summary view MUST include `pingan_bundle_step_source_name_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset step source-name counts are registry metadata only

- **WHEN** submit-once or PingAn resolved step `source:name` pairs are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, workflow-builder behavior, or complete execution-chain coverage

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle step-entry counts

`catalog validate` SHALL include additive `submit_once_bundle_step_entry_counts` and `pingan_bundle_step_entry_counts` objects derived from selected resolved bundle step entries without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset step-entry counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_step_entry_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_step_entry_counts`
- **AND** both fields MUST count resolved step entries from their matching bundle subsets

#### Scenario: Summary view preserves subset step-entry counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_step_entry_counts`
- **AND** the summary view MUST include `pingan_bundle_step_entry_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset step-entry counts are registry metadata only

- **WHEN** submit-once or PingAn resolved step entries are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, workflow-builder behavior, complete execution-chain coverage, or a full step manifest

### Requirement: Catalog validation SHALL expose task/report bundle step source-entry counts

`catalog validate` SHALL include additive `task_report_bundle_step_source_entry_counts` for selected resolved bundles that contain both task and report steps without executing task, report, trade, catalog entry, or bundle steps.

#### Scenario: Task/report bundle source-entry counts are included in detailed validation

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_source_entry_counts`
- **AND** keys MUST be `source:entry` strings derived from resolved task/report bundle steps
- **AND** the sum of `task_report_bundle_step_source_entry_counts` values MUST equal `task_report_bundle_step_count`
- **AND** validation MUST remain non-executing

#### Scenario: Non task/report selections have empty source-entry counts

- **WHEN** a caller validates selected bundles that do not contain both task and report steps
- **THEN** `task_report_bundle_step_source_entry_counts` MUST be an empty object

#### Scenario: Summary view preserves task/report source-entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_source_entry_counts`
- **AND** the summary payload MUST NOT include full bundle definitions

### Requirement: Catalog validation SHALL expose bundle step source-entry counts

`catalog validate` SHALL include additive `bundle_step_source_entry_counts` for selected resolved bundle steps without executing catalog entries, task entries, report entries, trade commands, or bundle steps.

#### Scenario: Bundle source-entry counts are included in detailed validation

- **WHEN** a caller validates selected catalog bundles
- **THEN** the validation payload MUST include `bundle_step_source_entry_counts`
- **AND** keys MUST be `source:entry` strings derived from selected resolved bundle steps
- **AND** the sum of `bundle_step_source_entry_counts` values MUST equal `bundle_step_count`
- **AND** validation MUST remain non-executing

#### Scenario: Non-bundle selections have empty source-entry counts

- **WHEN** a caller validates only catalog entries
- **THEN** `bundle_step_source_entry_counts` MUST be an empty object

#### Scenario: Summary view preserves bundle source-entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_entry_counts`
- **AND** the summary payload MUST NOT include full bundle definitions

### Requirement: Command catalog validate SHALL summarize selected bundle step source option keys

`catalog validate` SHALL include additive `bundle_step_source_option_key_counts` for selected resolved bundle steps without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts source option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_source_option_key_counts`
- **AND** each key MUST be formatted as `source:option_key`
- **AND** the sum of values MUST equal the sum of `bundle_step_option_key_counts` values for resolved steps with a source
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have empty source option-key counts

- **WHEN** a caller validates only catalog entries
- **THEN** `bundle_step_source_option_key_counts` MUST be an empty object

#### Scenario: Summary view preserves source option-key counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_option_key_counts`
- **AND** the summary payload MUST NOT include full bundle definitions

### Requirement: Command catalog validate SHALL summarize task/report step source option keys

`catalog validate` SHALL include additive `task_report_bundle_step_source_option_key_counts` for selected resolved bundles that contain both task and report steps without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts task/report source option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_source_option_key_counts`
- **AND** each key MUST be formatted as `source:option_key`
- **AND** the count map MUST be derived only from selected bundles that contain both task and report steps
- **AND** the sum of values MUST equal the sum of `task_report_bundle_step_option_key_counts` values for resolved task/report bundle steps with a source
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have empty task/report source option-key counts

- **WHEN** a caller validates only catalog entries
- **THEN** `task_report_bundle_step_source_option_key_counts` MUST be an empty object

#### Scenario: Summary view preserves task/report source option-key counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_source_option_key_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Command catalog validate SHALL summarize submit-once and PingAn step option keys

`catalog validate` SHALL include additive `submit_once_bundle_step_option_key_counts` and `pingan_bundle_step_option_key_counts` for selected resolved submit-once and PingAn bundle subsets without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts submit-once and PingAn option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `submit_once_bundle_step_option_key_counts`
- **AND** the validation payload MUST include `pingan_bundle_step_option_key_counts`
- **AND** each count map MUST be derived only from the matching selected resolved bundle subset
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have empty submit-once and PingAn option-key counts

- **WHEN** a caller validates only catalog entries
- **THEN** `submit_once_bundle_step_option_key_counts` MUST be an empty object
- **AND** `pingan_bundle_step_option_key_counts` MUST be an empty object

#### Scenario: Summary view preserves submit-once and PingAn option-key counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `submit_once_bundle_step_option_key_counts`
- **AND** the summary payload MUST include `pingan_bundle_step_option_key_counts`
- **AND** both summary values MUST mirror the detailed validation values
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Command catalog validate SHALL summarize submit-once and PingAn step source option keys

`catalog validate` SHALL include additive `submit_once_bundle_step_source_option_key_counts` and `pingan_bundle_step_source_option_key_counts` for selected resolved submit-once and PingAn bundle subsets without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts submit-once and PingAn source option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `submit_once_bundle_step_source_option_key_counts`
- **AND** the validation payload MUST include `pingan_bundle_step_source_option_key_counts`
- **AND** each key MUST be formatted as `source:option_key`
- **AND** each count map MUST be derived only from the matching selected resolved bundle subset
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have empty submit-once and PingAn source option-key counts

- **WHEN** a caller validates only catalog entries
- **THEN** `submit_once_bundle_step_source_option_key_counts` MUST be an empty object
- **AND** `pingan_bundle_step_source_option_key_counts` MUST be an empty object

#### Scenario: Summary view preserves submit-once and PingAn source option-key counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `submit_once_bundle_step_source_option_key_counts`
- **AND** the summary payload MUST include `pingan_bundle_step_source_option_key_counts`
- **AND** both summary values MUST mirror the detailed validation values
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Command catalog validate SHALL summarize submit-once and PingAn step counts

`catalog validate` SHALL include additive `submit_once_bundle_step_count` and `pingan_bundle_step_count` for selected resolved submit-once and PingAn bundle subsets without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts submit-once and PingAn steps

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `submit_once_bundle_step_count`
- **AND** the validation payload MUST include `pingan_bundle_step_count`
- **AND** each count MUST be derived only from the matching selected resolved bundle subset
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have zero submit-once and PingAn step counts

- **WHEN** a caller validates only catalog entries
- **THEN** `submit_once_bundle_step_count` MUST be `0`
- **AND** `pingan_bundle_step_count` MUST be `0`

#### Scenario: Summary view preserves submit-once and PingAn step counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `submit_once_bundle_step_count`
- **AND** the summary payload MUST include `pingan_bundle_step_count`
- **AND** both summary values MUST mirror the detailed validation values
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Command catalog validate SHALL summarize submit-once and PingAn step source entries

`catalog validate` SHALL include additive `submit_once_bundle_step_source_entry_counts` and `pingan_bundle_step_source_entry_counts` for selected resolved submit-once and PingAn bundle subsets without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts submit-once and PingAn source entries

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `submit_once_bundle_step_source_entry_counts`
- **AND** the validation payload MUST include `pingan_bundle_step_source_entry_counts`
- **AND** each key MUST be formatted as `source:entry`
- **AND** each count map MUST be derived only from the matching selected resolved bundle subset
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have empty submit-once and PingAn source-entry counts

- **WHEN** a caller validates only catalog entries
- **THEN** `submit_once_bundle_step_source_entry_counts` MUST be an empty object
- **AND** `pingan_bundle_step_source_entry_counts` MUST be an empty object

#### Scenario: Summary view preserves submit-once and PingAn source-entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `submit_once_bundle_step_source_entry_counts`
- **AND** the summary payload MUST include `pingan_bundle_step_source_entry_counts`
- **AND** both summary values MUST mirror the detailed validation values
- **AND** the summary payload MUST remain a read-only aggregate projection

### Requirement: Catalog summary SHALL expose bundle sample counts

Catalog summary views SHALL include read-only `task_report_bundle_sample_count`, `submit_once_bundle_sample_count`, and `pingan_bundle_sample_count` fields derived from their bounded visible sample arrays when those arrays are projected, without exposing full bundle manifests or executing catalog entries, bundle steps, task/report commands, submit-once flows, broker probes, or trade operations.

#### Scenario: Summary view includes task/report bundle sample count

- **WHEN** a caller requests a catalog summary view that includes `task_report_bundle_samples`
- **THEN** the summary result MUST include `task_report_bundle_sample_count` equal to the length of `task_report_bundle_samples`
- **AND** `task_report_bundle_count`, `task_report_bundle_step_count`, `task_report_bundle_sample_limit`, and `task_report_bundle_sample_truncated` MUST remain unchanged
- **AND** the summary MUST NOT execute task/report commands or bundle steps

#### Scenario: Summary view includes submit-once bundle sample count

- **WHEN** a caller requests a catalog summary view that includes `submit_once_bundle_samples`
- **THEN** the summary result MUST include `submit_once_bundle_sample_count` equal to the length of `submit_once_bundle_samples`
- **AND** `submit_once_bundle_count`, `submit_once_bundle_step_count`, `submit_once_bundle_sample_limit`, and `submit_once_bundle_sample_truncated` MUST remain unchanged
- **AND** the summary MUST NOT execute submit-once commands, broker probes, trade operations, or bundle steps

#### Scenario: Summary view includes PingAn bundle sample count

- **WHEN** a caller requests a catalog summary view that includes `pingan_bundle_samples`
- **THEN** the summary result MUST include `pingan_bundle_sample_count` equal to the length of `pingan_bundle_samples`
- **AND** `pingan_bundle_count`, `pingan_bundle_step_count`, `pingan_bundle_sample_limit`, and `pingan_bundle_sample_truncated` MUST remain unchanged
- **AND** the summary MUST NOT execute PingAn commands, broker probes, trade operations, or bundle steps

### Requirement: Catalog list summary SHALL expose available label counts

Catalog list summary views SHALL include read-only `available_entry_label_count` and `available_bundle_label_count` fields derived from their projected available label arrays when those arrays are present, without exposing full execution behavior or executing catalog entries, bundle steps, task/report commands, submit-once flows, broker probes, or trade operations.

#### Scenario: Entry list summary includes available entry label count

- **WHEN** a caller requests `catalog list --kind entry --view summary` and the result includes `available_entry_labels`
- **THEN** the summary result MUST include `available_entry_label_count` equal to the length of `available_entry_labels`
- **AND** `entry_count`, `matched_entry_count`, and `available_entry_labels` MUST remain unchanged
- **AND** the summary MUST NOT execute catalog entries, task/report commands, broker probes, trade operations, or bundle steps

#### Scenario: Bundle list summary includes available bundle label count

- **WHEN** a caller requests `catalog list --kind bundle --view summary` and the result includes `available_bundle_labels`
- **THEN** the summary result MUST include `available_bundle_label_count` equal to the length of `available_bundle_labels`
- **AND** `bundle_count`, `matched_bundle_count`, and `available_bundle_labels` MUST remain unchanged
- **AND** the summary MUST NOT execute catalog entries, bundle steps, task/report commands, broker probes, or trade operations

### Requirement: Catalog Validate Step Source Key Counts

Catalog validate summary view SHALL expose read-only step source key-count fields derived from already projected source-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes bundle step source key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_source_counts`
- **THEN** the summary view MUST include `bundle_step_source_key_count` equal to the number of keys in `bundle_step_source_counts`
- **AND** this field MUST count distinct source keys, not resolved steps.

#### Scenario: Summary includes task/report bundle step source key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_source_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_source_key_count` equal to the number of keys in `task_report_bundle_step_source_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Bundle Label Key Counts

Catalog validate summary view SHALL expose read-only bundle label key-count fields derived from already projected label-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes bundle label key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_label_counts`
- **THEN** the summary view MUST include `bundle_label_key_count` equal to the number of keys in `bundle_label_counts`
- **AND** this field MUST count distinct label keys, not bundles.

#### Scenario: Summary includes task/report bundle label key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_label_counts`
- **THEN** the summary view MUST include `task_report_bundle_label_key_count` equal to the number of keys in `task_report_bundle_label_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Submit/PingAn Label Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle label key-count fields derived from already projected subset label-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle label key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_label_counts`
- **THEN** the summary view MUST include `submit_once_bundle_label_key_count` equal to the number of keys in `submit_once_bundle_label_counts`
- **AND** this field MUST count distinct label keys, not bundles.

#### Scenario: Summary includes PingAn bundle label key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_label_counts`
- **THEN** the summary view MUST include `pingan_bundle_label_key_count` equal to the number of keys in `pingan_bundle_label_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Submit/PingAn Step Source Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle step source key-count fields derived from already projected subset step source-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle step source key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_step_source_counts`
- **THEN** the summary view MUST include `submit_once_bundle_step_source_key_count` equal to the number of keys in `submit_once_bundle_step_source_counts`
- **AND** this field MUST count distinct source keys, not resolved steps.

#### Scenario: Summary includes PingAn bundle step source key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_step_source_counts`
- **THEN** the summary view MUST include `pingan_bundle_step_source_key_count` equal to the number of keys in `pingan_bundle_step_source_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Submit/PingAn Step Name Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle step name key-count fields derived from already projected subset step name-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle step name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_step_name_counts`
- **THEN** the summary view MUST include `submit_once_bundle_step_name_key_count` equal to the number of keys in `submit_once_bundle_step_name_counts`
- **AND** this field MUST count distinct step-name keys, not resolved steps.

#### Scenario: Summary includes PingAn bundle step name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_step_name_counts`
- **THEN** the summary view MUST include `pingan_bundle_step_name_key_count` equal to the number of keys in `pingan_bundle_step_name_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Submit/PingAn Step Source-Name Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle step source-name key-count fields derived from already projected subset step `source:name` count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle step source-name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_step_source_name_counts`
- **THEN** the summary view MUST include `submit_once_bundle_step_source_name_key_count` equal to the number of keys in `submit_once_bundle_step_source_name_counts`
- **AND** this field MUST count distinct `source:name` keys, not resolved steps.

#### Scenario: Summary includes PingAn bundle step source-name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_step_source_name_counts`
- **THEN** the summary view MUST include `pingan_bundle_step_source_name_key_count` equal to the number of keys in `pingan_bundle_step_source_name_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Submit/PingAn Step Entry Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle step entry key-count fields derived from already projected subset step entry-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle step entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_step_entry_counts`
- **THEN** the summary view MUST include `submit_once_bundle_step_entry_key_count` equal to the number of keys in `submit_once_bundle_step_entry_counts`
- **AND** this field MUST count distinct step-entry keys, not resolved steps.

#### Scenario: Summary includes PingAn bundle step entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_step_entry_counts`
- **THEN** the summary view MUST include `pingan_bundle_step_entry_key_count` equal to the number of keys in `pingan_bundle_step_entry_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Submit/PingAn Step Source-Entry Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle step source-entry key-count fields derived from already projected subset step `source:entry` count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle step source-entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_step_source_entry_counts`
- **THEN** the summary view MUST include `submit_once_bundle_step_source_entry_key_count` equal to the number of keys in `submit_once_bundle_step_source_entry_counts`
- **AND** this field MUST count distinct `source:entry` keys, not resolved steps.

#### Scenario: Summary includes PingAn bundle step source-entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_step_source_entry_counts`
- **THEN** the summary view MUST include `pingan_bundle_step_source_entry_key_count` equal to the number of keys in `pingan_bundle_step_source_entry_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Submit/PingAn Step Option-Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle step option-key count fields derived from already projected subset step option-key count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle step option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_step_option_key_counts`
- **THEN** the summary view MUST include `submit_once_bundle_step_option_key_count` equal to the number of keys in `submit_once_bundle_step_option_key_counts`
- **AND** this field MUST count distinct option keys, not resolved steps or option values.

#### Scenario: Summary includes PingAn bundle step option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_step_option_key_counts`
- **THEN** the summary view MUST include `pingan_bundle_step_option_key_count` equal to the number of keys in `pingan_bundle_step_option_key_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Submit/PingAn Step Source-Option-Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle step source-option-key count fields derived from already projected subset step `source:option_key` count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle step source-option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_step_source_option_key_counts`
- **THEN** the summary view MUST include `submit_once_bundle_step_source_option_key_count` equal to the number of keys in `submit_once_bundle_step_source_option_key_counts`
- **AND** this field MUST count distinct `source:option_key` keys, not resolved steps or option values.

#### Scenario: Summary includes PingAn bundle step source-option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_step_source_option_key_counts`
- **THEN** the summary view MUST include `pingan_bundle_step_source_option_key_count` equal to the number of keys in `pingan_bundle_step_source_option_key_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Entry Source/Label Key Counts

Catalog validate summary view SHALL expose read-only entry source and entry label key-count fields derived from already projected entry count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes entry source key count

- **GIVEN** a caller validates catalog entries with `--view summary`
- **WHEN** the summary view includes `entry_source_counts`
- **THEN** the summary view MUST include `entry_source_key_count` equal to the number of keys in `entry_source_counts`
- **AND** this field MUST count distinct projected entry source keys, not matched entries or executed entries.

#### Scenario: Summary includes entry label key count

- **GIVEN** a caller validates catalog entries with `--view summary`
- **WHEN** the summary view includes `entry_label_counts`
- **THEN** the summary view MUST include `entry_label_key_count` equal to the number of keys in `entry_label_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Step Name/Entry Key Counts

Catalog validate summary view SHALL expose read-only selected bundle and task+report bundle step name/entry key-count fields derived from already projected step count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes selected bundle step name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_name_counts`
- **THEN** the summary view MUST include `bundle_step_name_key_count` equal to the number of keys in `bundle_step_name_counts`
- **AND** this field MUST count distinct projected step names, not resolved steps or executed steps.

#### Scenario: Summary includes selected bundle step entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_entry_counts`
- **THEN** the summary view MUST include `bundle_step_entry_key_count` equal to the number of keys in `bundle_step_entry_counts`
- **AND** this field MUST count distinct projected step entry keys, not resolved steps or executed steps.

#### Scenario: Summary includes task+report bundle step name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_name_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_name_key_count` equal to the number of keys in `task_report_bundle_step_name_counts`
- **AND** this field MUST count distinct projected task+report step names, not resolved steps or executed steps.

#### Scenario: Summary includes task+report bundle step entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_entry_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_entry_key_count` equal to the number of keys in `task_report_bundle_step_entry_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Step Source-Name/Source-Entry Key Counts

Catalog validate summary view SHALL expose read-only selected bundle and task+report bundle source-qualified step name/entry key-count fields derived from already projected step count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes selected bundle step source-name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_source_name_counts`
- **THEN** the summary view MUST include `bundle_step_source_name_key_count` equal to the number of keys in `bundle_step_source_name_counts`
- **AND** this field MUST count distinct projected `source:name` keys, not resolved steps or executed steps.

#### Scenario: Summary includes selected bundle step source-entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_source_entry_counts`
- **THEN** the summary view MUST include `bundle_step_source_entry_key_count` equal to the number of keys in `bundle_step_source_entry_counts`
- **AND** this field MUST count distinct projected `source:entry` keys, not resolved steps or executed steps.

#### Scenario: Summary includes task+report bundle step source-name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_source_name_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_source_name_key_count` equal to the number of keys in `task_report_bundle_step_source_name_counts`
- **AND** this field MUST count distinct projected task+report `source:name` keys, not resolved steps or executed steps.

#### Scenario: Summary includes task+report bundle step source-entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_source_entry_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_source_entry_key_count` equal to the number of keys in `task_report_bundle_step_source_entry_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.

### Requirement: Catalog Validate Bundle/Task-Report Option-Key Counts

Catalog validate summary view SHALL expose read-only selected bundle and task+report option-key/source-option-key key-count fields derived from already projected step option count maps, without exposing option values or executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes selected bundle step option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_option_key_counts`
- **THEN** the summary view MUST include `bundle_step_option_key_count` equal to the number of keys in `bundle_step_option_key_counts`
- **AND** this field MUST count distinct projected option keys, not resolved steps or option values.

#### Scenario: Summary includes selected bundle step source-option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_source_option_key_counts`
- **THEN** the summary view MUST include `bundle_step_source_option_key_count` equal to the number of keys in `bundle_step_source_option_key_counts`
- **AND** this field MUST count distinct projected `source:option_key` keys, not resolved steps or option values.

#### Scenario: Summary includes task+report bundle step option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_option_key_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_option_key_count` equal to the number of keys in `task_report_bundle_step_option_key_counts`
- **AND** this field MUST count distinct projected task+report option keys, not resolved steps or option values.

#### Scenario: Summary includes task+report bundle step source-option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_source_option_key_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_source_option_key_count` equal to the number of keys in `task_report_bundle_step_source_option_key_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, option semantic validation, or trading safety.

### Requirement: Command catalog plan and preview summary SHALL expose step source key count

Command catalog bundle plan and preview summary views SHALL include additive read-only `step_source_key_count` derived from the existing `step_source_counts` map for selected resolved bundle steps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Caller plans a mixed bundle summary

- **WHEN** a caller executes `catalog plan --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_source_counts`
- **AND** the summary view MUST include `step_source_key_count` equal to the number of keys in `step_source_counts`
- **AND** `step_source_key_count` MUST count distinct selected step sources, not selected steps

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary` with step filtering
- **THEN** the summary view MUST include `step_source_counts` for the selected filtered steps
- **AND** `step_source_key_count` MUST equal the number of keys in that filtered `step_source_counts` map

#### Scenario: Step source key count remains non-executing

- **WHEN** a caller inspects a catalog plan or preview summary
- **THEN** `step_source_key_count` MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the field MUST NOT be treated as workflow execution coverage, provider readiness, broker readiness, or trade safety proof

### Requirement: Command catalog plan and preview summary SHALL expose step name counts

Command catalog bundle plan and preview summary views SHALL include additive read-only `step_name_counts` and `step_name_key_count` fields derived from selected resolved bundle steps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Caller plans a mixed bundle summary

- **WHEN** a caller executes `catalog plan --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_name_counts` for selected resolved step names
- **AND** the summary view MUST include `step_name_key_count` equal to the number of keys in `step_name_counts`
- **AND** `selected_step_count` MUST remain the selected resolved step total

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary` with step filtering
- **THEN** the summary view MUST include `step_name_counts` for the selected filtered steps
- **AND** `step_name_key_count` MUST equal the number of keys in that filtered `step_name_counts` map

#### Scenario: Step name counts remain non-executing

- **WHEN** a caller inspects a catalog plan or preview summary
- **THEN** `step_name_counts` and `step_name_key_count` MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the fields MUST NOT be treated as a complete step manifest, workflow execution coverage, provider readiness, broker readiness, or trade safety proof

### Requirement: Command catalog plan and preview summary SHALL expose step entry counts

Command catalog bundle plan and preview summary views SHALL include additive read-only `step_entry_counts` and `step_entry_key_count` fields derived from selected resolved bundle steps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Caller plans a mixed bundle summary

- **WHEN** a caller executes `catalog plan --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_entry_counts` for selected resolved step entries
- **AND** the summary view MUST include `step_entry_key_count` equal to the number of keys in `step_entry_counts`
- **AND** `selected_step_count` MUST remain the selected resolved step total

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary` with step filtering
- **THEN** the summary view MUST include `step_entry_counts` for the selected filtered steps
- **AND** `step_entry_key_count` MUST equal the number of keys in that filtered `step_entry_counts` map

#### Scenario: Step entry counts remain non-executing

- **WHEN** a caller inspects a catalog plan or preview summary
- **THEN** `step_entry_counts` and `step_entry_key_count` MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the fields MUST NOT be treated as a complete step manifest, workflow execution coverage, provider readiness, broker readiness, or trade safety proof

### Requirement: Command catalog plan and preview summary SHALL expose step source-name counts

Command catalog bundle plan and preview summary views SHALL include additive read-only `step_source_name_counts` and `step_source_name_key_count` fields derived from selected resolved bundle step `source:name` pairs without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Caller plans a mixed bundle summary

- **WHEN** a caller executes `catalog plan --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_source_name_counts` for selected resolved step `source:name` pairs
- **AND** the summary view MUST include `step_source_name_key_count` equal to the number of keys in `step_source_name_counts`
- **AND** `selected_step_count` MUST remain the selected resolved step total

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary` with step filtering
- **THEN** the summary view MUST include `step_source_name_counts` for the selected filtered steps
- **AND** `step_source_name_key_count` MUST equal the number of keys in that filtered `step_source_name_counts` map

#### Scenario: Step source-name counts remain non-executing

- **WHEN** a caller inspects a catalog plan or preview summary
- **THEN** `step_source_name_counts` and `step_source_name_key_count` MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the fields MUST NOT be treated as a complete step manifest, workflow execution coverage, provider readiness, broker readiness, or trade safety proof

### Requirement: Command catalog plan and preview summary SHALL expose step source-entry counts

Command catalog bundle plan and preview summary views SHALL include additive read-only `step_source_entry_counts` and `step_source_entry_key_count` fields derived from selected resolved bundle step `source:entry` pairs without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Caller plans a mixed bundle summary

- **WHEN** a caller executes `catalog plan --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_source_entry_counts` for selected resolved step `source:entry` pairs
- **AND** the summary view MUST include `step_source_entry_key_count` equal to the number of keys in `step_source_entry_counts`
- **AND** `selected_step_count` MUST remain the selected resolved step total

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary` with step filtering
- **THEN** the summary view MUST include `step_source_entry_counts` for the selected filtered steps
- **AND** `step_source_entry_key_count` MUST equal the number of keys in that filtered `step_source_entry_counts` map

#### Scenario: Step source-entry counts remain non-executing

- **WHEN** a caller inspects a catalog plan or preview summary
- **THEN** `step_source_entry_counts` and `step_source_entry_key_count` MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the fields MUST NOT be treated as a complete step manifest, workflow execution coverage, provider readiness, broker readiness, or trade safety proof

### Requirement: Catalog bundle plan summary SHALL expose selected step resolved-arg key counts

The command catalog SHALL include additive read-only `step_resolved_arg_key_counts`, `step_resolved_arg_key_count`, `step_source_resolved_arg_key_counts`, and `step_source_resolved_arg_key_count` fields in bundle `catalog plan` and `catalog preview` summary views, derived only from selected steps' resolved argument maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Bundle preview summary includes resolved-arg key counts

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_resolved_arg_key_counts` for resolved argument keys present on selected steps
- **AND** the summary view MUST include `step_resolved_arg_key_count` equal to the number of distinct resolved argument keys
- **AND** the summary view MUST include `step_source_resolved_arg_key_counts` using `<source>:<key>` keys
- **AND** the summary view MUST include `step_source_resolved_arg_key_count` equal to the number of distinct source-qualified resolved argument keys
- **AND** the summary view MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Selected step range scopes resolved-arg key counts

- **WHEN** a caller executes `catalog plan --bundle <bundle> --only-step <step> --view summary`
- **THEN** the resolved-arg key count maps MUST be derived only from the selected step range
- **AND** the maps MUST not count unselected bundle steps
- **AND** existing non-execution provenance, constraints, step source/name/entry count maps, and reduced step projection behavior MUST remain unchanged

### Requirement: Catalog validation summary SHALL expose task/report bundle summary

Command catalog validation summary views SHALL include additive read-only `task_report_bundle_summary` metadata derived from existing task/report bundle validation counts and maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Validation summary includes compact task/report bundle metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label <label> --view summary`
- **THEN** the summary view MUST include `task_report_bundle_summary.count` matching `task_report_bundle_count`
- **AND** it MUST include `step_count`, `sample_count`, `sample_limit`, and `sample_truncated` matching the existing task/report bundle sibling fields
- **AND** it MUST include label and step-map key counts derived from the corresponding projected count maps
- **AND** existing task/report bundle sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Validation summary handles no task/report bundles

- **WHEN** a catalog validation summary selection has no task/report bundles
- **THEN** `task_report_bundle_summary.count` MUST be `0`
- **AND** sample and map key counts MUST be `0`
- **AND** `sample_truncated` MUST be falsey or `false`
- **AND** the summary MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof

### Requirement: Catalog validation summary SHALL expose bundle step summary

Command catalog validation summary views SHALL include additive read-only `bundle_step_summary` metadata derived from existing selected-bundle validation counts and maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Validation summary includes compact selected-bundle step metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label <label> --view summary`
- **THEN** the summary view MUST include `bundle_step_summary.bundle_count` matching `bundle_count`
- **AND** it MUST include `step_count` matching `bundle_step_count`
- **AND** it MUST include label and step-map key counts derived from the corresponding projected count maps
- **AND** existing selected-bundle sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Validation summary handles no selected bundles

- **WHEN** a catalog validation summary selection has no selected bundles
- **THEN** `bundle_step_summary.bundle_count` MUST be `0`
- **AND** `step_count` and map key counts MUST be `0`
- **AND** the summary MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof

### Requirement: Catalog validation summary SHALL expose entry summary

Command catalog validation summary views SHALL include additive read-only `entry_summary` metadata derived from existing selected-entry validation counts and maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Validation summary includes compact selected-entry metadata

- **WHEN** a caller runs `catalog validate --kind entry --label <label> --view summary`
- **THEN** the summary view MUST include `entry_summary.count` matching `entry_count`
- **AND** it MUST include `source_key_count` and `label_key_count` derived from the corresponding projected count maps
- **AND** existing selected-entry sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full entry manifests, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Validation summary handles no selected entries

- **WHEN** a catalog validation summary selection has no selected entries
- **THEN** `entry_summary.count` MUST be `0`
- **AND** `source_key_count` and `label_key_count` MUST be `0`
- **AND** the summary MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof

### Requirement: Catalog validation summary SHALL expose submit-once and PingAn bundle summaries

Command catalog validation summary views SHALL include additive read-only `submit_once_bundle_summary` and `pingan_bundle_summary` metadata derived from existing submit-once/PingAn bundle validation counts and maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Validation summary includes compact submit-once bundle metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label submit-once --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_summary.count` matching `submit_once_bundle_count`
- **AND** it MUST include `step_count`, `sample_count`, `sample_limit`, and `sample_truncated` derived from the corresponding projected submit-once sibling fields
- **AND** it MUST include label/source/name/entry/option key-count fields derived from the corresponding projected submit-once sibling fields
- **AND** existing submit-once sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full entry manifests, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Validation summary includes compact PingAn bundle metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label pingan --view summary`
- **THEN** the summary view MUST include `pingan_bundle_summary.count` matching `pingan_bundle_count`
- **AND** it MUST include `step_count`, `sample_count`, `sample_limit`, and `sample_truncated` derived from the corresponding projected PingAn sibling fields
- **AND** it MUST include label/source/name/entry/option key-count fields derived from the corresponding projected PingAn sibling fields
- **AND** existing PingAn sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full entry manifests, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Validation summary handles no submit-once or PingAn bundles

- **WHEN** a catalog validation summary selection has no matching submit-once or PingAn bundles
- **THEN** the corresponding compact summary `count` MUST be `0`
- **AND** `step_count`, sample metadata, and map key counts MUST remain deterministic zero/empty-derived values
- **AND** the summary MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof

### Requirement: Catalog validate summary SHALL expose validation outcome

`catalog validate --view summary` SHALL include additive read-only `validation_outcome` metadata derived from existing validation summary fields without executing catalog entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.

#### Scenario: Bundle validation summary includes outcome

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `validation_outcome`
- **AND** the object MUST derive kind, selected label, entry count, bundle count, invalid count, validity, non-execution flag, result code, and result message from existing summary siblings
- **AND** `has_invalid_entries` MUST be false when the existing invalid count is zero
- **AND** the summary MUST NOT include raw `entries` or raw `bundles`

#### Scenario: Outcome remains non-executing

- **WHEN** catalog validation reports `validation_outcome`
- **THEN** the object MUST NOT indicate that any entry, bundle, task/report step, trade command, provider call, or workflow action was executed
- **AND** existing count maps and family summary objects MUST remain available

### Requirement: Catalog plan summary SHALL expose plan outcome

`catalog plan --view summary` and `catalog preview --view summary` SHALL include additive read-only `plan_outcome` metadata derived from existing plan summary fields and non-execution constraints without executing catalog entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.

#### Scenario: Bundle plan summary includes outcome

- **WHEN** a caller runs `catalog plan --bundle confirm-complete-review --view summary`
- **THEN** the summary payload MUST include `plan_outcome`
- **AND** the object MUST derive mode, target type/name, selected step count, step-source key count, result code, and result message from existing summary siblings
- **AND** `non_execution` MUST be true only when existing constraints indicate non-executing mode and no dispatch execution
- **AND** existing `constraints`, `steps`, step count maps, and summary fields MUST remain available

#### Scenario: Plan outcome remains non-executing

- **WHEN** catalog plan or preview reports `plan_outcome`
- **THEN** the object MUST NOT indicate that any entry, bundle, task/report step, trade command, provider call, or workflow action was executed
- **AND** the summary MUST NOT claim workflow-builder support, broker readiness, trade safety approval, or execution coverage
