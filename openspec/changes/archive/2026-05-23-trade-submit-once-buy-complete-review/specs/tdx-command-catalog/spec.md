## ADDED Requirements

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
