## ADDED Requirements

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
