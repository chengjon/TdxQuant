## ADDED Requirements

### Requirement: Stable desktop trading SHALL expose a read-only dialog readiness workflow
The system SHALL expose a stable non-side-effecting workflow that checks whether the current confirm/result dialogs can be located through the stable desktop trade lookup path.

#### Scenario: Caller checks confirm dialog readiness
- **WHEN** a caller executes `TdxTradeManager.pingan.dialog_readiness(...)` for the confirm dialog
- **THEN** the result MUST include a structured readiness summary for the requested dialog target

#### Scenario: Caller checks result dialog readiness
- **WHEN** a caller executes the stable dialog readiness workflow for the result dialog
- **THEN** the summary MUST include the result-dialog lookup outcome and the result confirm-button lookup outcome

### Requirement: Stable desktop trading dialog readiness SHALL support passive and required visibility semantics
The system SHALL let callers choose whether currently absent dialogs are treated as warnings or failures.

#### Scenario: Caller observes dialog readiness without requiring visibility
- **WHEN** a caller executes the stable dialog readiness workflow without `require_visible`
- **THEN** an absent requested dialog MUST be reported as a warning-style readiness outcome

#### Scenario: Caller requires current dialog visibility
- **WHEN** a caller executes the stable dialog readiness workflow with `require_visible`
- **THEN** an absent requested dialog MUST be reported as a failed-style readiness outcome

### Requirement: Stable desktop trading dialog readiness SHALL remain non-side-effecting
The system SHALL keep the stable dialog readiness workflow read-only.

#### Scenario: Dialog readiness does not mutate runtime state
- **WHEN** a caller executes the stable dialog readiness workflow
- **THEN** the workflow MUST NOT click any dialog control
- **AND** it MUST NOT close any dialog
- **AND** it MUST NOT write execution artifacts
