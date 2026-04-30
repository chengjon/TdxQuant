## ADDED Requirements

### Requirement: Stable desktop trading SHALL expose a pre-confirm submit-ready workflow
The system SHALL expose a stable side-effecting workflow that submits the current Ping An buy form up to the visible confirm dialog boundary without advancing the confirm action.

#### Scenario: Caller reaches the confirm boundary successfully
- **WHEN** a caller executes `TdxTradeManager.pingan.submit_ready(...)`
- **THEN** the workflow MUST perform the submit action
- **AND** the result MUST include a structured `submit_ready` summary
- **AND** the summary MUST indicate that manual confirmation is still required

### Requirement: Stable desktop trading submit-ready SHALL verify confirm visibility through the stable lookup path
The system SHALL validate the current confirm dialog through the stable confirm lookup rules after the submit action.

#### Scenario: Caller uses the default UIA confirm lookup
- **WHEN** a caller executes the stable submit-ready workflow with the default lookup mode
- **THEN** the workflow MUST validate the visible confirm dialog through the UIA lookup path

#### Scenario: Caller uses experimental Win32 confirm lookup
- **WHEN** a caller executes the stable submit-ready workflow with `dialog_lookup_mode=win32_experimental`
- **THEN** the workflow MUST validate the visible confirm dialog through the experimental Win32 lookup path with the existing UIA fallback semantics

#### Scenario: Confirm dialog is not detected after submit
- **WHEN** a caller executes the stable submit-ready workflow
- **AND** the stable confirm lookup path cannot detect the current confirm dialog
- **THEN** the workflow MUST return a failed-style result
- **AND** the result MUST include the confirm lookup detail

### Requirement: Stable desktop trading submit-ready SHALL stop before live confirmation side effects
The system SHALL keep the stable submit-ready workflow at the pre-confirm boundary.

#### Scenario: Submit-ready does not advance confirmation
- **WHEN** a caller executes the stable submit-ready workflow
- **THEN** the workflow MUST NOT click the current confirm dialog
- **AND** it MUST NOT close any result dialog

#### Scenario: Submit-ready does not write live-trade artifacts
- **WHEN** a caller executes the stable submit-ready workflow
- **THEN** the workflow MUST NOT write the last-order state artifact
- **AND** it MUST NOT append an order event log row
- **AND** it MUST NOT append a submission ledger row

### Requirement: Stable desktop trading submit-ready SHALL expose pre-confirm safety classification
The system SHALL expose normalized trade safety metadata for the stable submit-ready workflow while distinguishing it from live confirmed trade execution.

#### Scenario: Submit-ready returns local-state side-effect classification
- **WHEN** a caller executes the stable submit-ready workflow
- **THEN** the result `data.trade_safety` MUST be present
- **AND** `data.trade_safety.side_effect_level` MUST equal `local_state_mutating`
- **AND** `data.trade_safety.risk_gate` MUST describe the pre-trade request validation outcome

#### Scenario: Submit-ready rejects failed pre-trade risk gates before UI side effects
- **WHEN** a caller executes the stable submit-ready workflow with an invalid request or a rejected `max_price`
- **THEN** the workflow MUST return an invalid-request style result
- **AND** the desktop submit routine MUST NOT be called
