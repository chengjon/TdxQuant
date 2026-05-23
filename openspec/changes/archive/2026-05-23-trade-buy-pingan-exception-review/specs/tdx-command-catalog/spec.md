## ADDED Requirements

### Requirement: Command catalog SHALL expose ordinary buy PingAn exception bundles
The command catalog SHALL expose ordinary buy PingAn exception, rejection, and failure bundles that compose existing task and report entries without changing the underlying execution path.

#### Scenario: Caller plans ordinary buy PingAn exception review
- **WHEN** a caller plans `buy-pingan-exception-review`
- **THEN** the bundle MUST resolve its trade step through `task-buy`
- **AND** the bundle MUST resolve its audit step through `audit-daily-pingan-buy-exceptions`
- **AND** planning MUST NOT execute the task or report steps

#### Scenario: Caller plans ordinary buy PingAn rejection review
- **WHEN** a caller plans `buy-pingan-rejection-review`
- **THEN** the bundle MUST resolve its trade step through `task-buy`
- **AND** the bundle MUST resolve its audit step through `audit-daily-pingan-buy-rejected`

#### Scenario: Caller plans ordinary buy PingAn failure review
- **WHEN** a caller plans `buy-pingan-failure-review`
- **THEN** the bundle MUST resolve its trade step through `task-buy`
- **AND** the bundle MUST resolve its audit step through `audit-daily-pingan-buy-failed`

#### Scenario: Existing guarded-buy bundles remain available
- **WHEN** the ordinary buy bundles are registered
- **THEN** existing guarded-buy PingAn bundles MUST remain available
- **AND** the new bundles MUST NOT replace or remove guarded-buy catalog behavior
