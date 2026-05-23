## ADDED Requirements

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
