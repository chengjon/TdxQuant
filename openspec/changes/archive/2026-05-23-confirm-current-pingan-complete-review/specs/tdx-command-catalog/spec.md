## ADDED Requirements

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
