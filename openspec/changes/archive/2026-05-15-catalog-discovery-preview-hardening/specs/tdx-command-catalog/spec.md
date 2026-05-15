## ADDED Requirements

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
