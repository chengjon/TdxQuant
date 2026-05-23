## ADDED Requirements

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
