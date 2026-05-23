## ADDED Requirements

### Requirement: Command catalog SHALL expose explicit buy submit-once task entry and follow-up bundles
The command catalog SHALL expose a side-explicit buy submit-once task entry and buy-scoped PingAn follow-up bundles while continuing to route execution through existing `trade-submit-once` task behavior.

#### Scenario: Caller lists buy submit-once task entry
- **WHEN** a caller lists catalog entries with a `buy-submit-once` label
- **THEN** the catalog MUST include `task-buy-submit-once`
- **AND** the entry MUST resolve to a task preset whose command is `trade-submit-once` and whose options include `side=buy`

#### Scenario: Caller plans buy submit-once PingAn follow-up bundle
- **WHEN** a caller plans `buy-submit-once-pingan-exception-review`
- **THEN** the bundle MUST resolve a trade step through `task-buy-submit-once`
- **AND** the audit step MUST resolve through an existing PingAn buy submit-once audit report entry
- **AND** planning MUST NOT execute the trade or report steps

#### Scenario: Existing default submit-once entries remain available
- **WHEN** the explicit buy entry is registered
- **THEN** existing `submit-once` and `task-submit-once` catalog entries MUST remain present
- **AND** existing `task-sell-submit-once` behavior MUST remain side-scoped to sell
