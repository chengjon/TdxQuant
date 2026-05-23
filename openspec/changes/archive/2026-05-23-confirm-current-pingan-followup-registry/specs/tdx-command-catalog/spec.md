## ADDED Requirements

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
