## ADDED Requirements

### Requirement: Command catalog SHALL expose PingAn trade preflight readiness entry
The command catalog SHALL expose a PingAn trade preflight readiness entry for discovery and non-executing planning while reusing the existing read-only `trade preflight` workflow.

#### Scenario: Caller lists the preflight readiness entry
- **WHEN** a caller lists catalog entries with a `preflight` label
- **THEN** the catalog MUST include `trade-preflight-pingan-readiness`
- **AND** the entry MUST resolve to a trade preset whose command is `preflight`

#### Scenario: Caller plans the preflight readiness entry
- **WHEN** a caller plans `trade-preflight-pingan-readiness`
- **THEN** the plan summary MUST include trade input boundary metadata for the `preflight` command
- **AND** the boundary MUST identify the workflow as read-only preflight readiness input coverage
- **AND** planning MUST NOT execute the trade preflight workflow

#### Scenario: Missing order-shaped preflight inputs are explicit
- **WHEN** a caller plans `trade-preflight-pingan-readiness` without order inputs
- **THEN** the plan summary MUST report missing `code`, `price`, and `quantity`
- **AND** the plan summary MUST keep the non-execution constraints intact

