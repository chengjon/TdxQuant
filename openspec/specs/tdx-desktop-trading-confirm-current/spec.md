# tdx-desktop-trading-confirm-current Specification

## Purpose
TBD - created by archiving change add-trade-confirm-current-workflow. Update Purpose after archive.
## Requirements
### Requirement: Stable desktop trading SHALL expose a current-confirm workflow
The system SHALL expose a stable live-side-effecting workflow that advances the currently visible Ping An confirm dialog without re-submitting a new order request.

#### Scenario: Caller advances the current confirm dialog
- **WHEN** a caller executes `TdxTradeManager.pingan.confirm_current(...)`
- **THEN** the workflow MUST attempt to locate the currently visible confirm dialog
- **AND** it MUST attempt to advance that confirm dialog through the stable runtime click path

### Requirement: Stable desktop trading confirm-current SHALL reuse stable confirm lookup semantics
The system SHALL validate the current confirm dialog through the stable confirm lookup rules before clicking it.

#### Scenario: Caller uses the default UIA confirm lookup
- **WHEN** a caller executes the stable confirm-current workflow with the default lookup mode
- **THEN** the workflow MUST validate the current confirm dialog through the UIA lookup path

#### Scenario: Caller uses experimental Win32 confirm lookup
- **WHEN** a caller executes the stable confirm-current workflow with `dialog_lookup_mode=win32_experimental`
- **THEN** the workflow MUST validate the current confirm dialog through the experimental Win32 lookup path with the existing UIA fallback semantics

#### Scenario: Confirm dialog is not detected
- **WHEN** a caller executes the stable confirm-current workflow
- **AND** the stable confirm lookup path cannot detect the current confirm dialog
- **THEN** the workflow MUST return a failed-style result
- **AND** it MUST NOT attempt the confirm click

### Requirement: Stable desktop trading confirm-current SHALL summarize the current result-dialog boundary
The system SHALL summarize the current result-dialog boundary after the confirm click.

#### Scenario: Result dialog is detected after confirmation
- **WHEN** a caller executes the stable confirm-current workflow
- **AND** the current result dialog becomes visible
- **THEN** the result MUST include a structured result-dialog summary

#### Scenario: Result dialog is not detected after confirmation
- **WHEN** a caller executes the stable confirm-current workflow
- **AND** the current result dialog is not detected within the configured timeout
- **THEN** the workflow MUST report a warning-style readiness outcome instead of downgrading the confirm click itself to failed

### Requirement: Stable desktop trading confirm-current SHALL support optional result-dialog closeout
The system SHALL support optional automatic result-dialog closeout for the current result dialog.

#### Scenario: Caller keeps the current result dialog open
- **WHEN** a caller executes the stable confirm-current workflow with result closeout disabled
- **THEN** the workflow MUST NOT attempt to close the result dialog

#### Scenario: Caller requests automatic result-dialog closeout
- **WHEN** a caller executes the stable confirm-current workflow with result closeout enabled
- **THEN** the workflow MUST attempt to locate the current result confirm control
- **AND** it MUST attempt to close the result dialog through the stable runtime click path

### Requirement: Stable desktop trading confirm-current SHALL persist confirmed-trade artifacts without ledger semantics
The system SHALL persist standard confirmed-trade artifacts for the current-confirm workflow while excluding submission-ledger behavior.

#### Scenario: Confirm-current writes confirmed-trade artifacts
- **WHEN** a caller executes the stable confirm-current workflow and the confirm click succeeds
- **THEN** the workflow MUST write the standardized last-order state artifact
- **AND** it MUST append the standardized order event row

#### Scenario: Confirm-current does not write a submission ledger row
- **WHEN** a caller executes the stable confirm-current workflow
- **THEN** the workflow MUST NOT append a submission-ledger row

### Requirement: Stable desktop trading confirm-current SHALL expose live-side-effecting safety classification
The system SHALL expose normalized trade safety metadata for the current-confirm workflow.

#### Scenario: Confirm-current returns live-side-effecting safety metadata
- **WHEN** a caller executes the stable confirm-current workflow
- **THEN** the result `data.trade_safety` MUST be present
- **AND** `data.trade_safety.side_effect_level` MUST equal `live_side_effecting`

