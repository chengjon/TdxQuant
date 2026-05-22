## ADDED Requirements

### Requirement: Command catalog SHALL expose the desktop broker capability probe as a non-executing entry
The command catalog SHALL include a stable entry for the PingAn desktop extended broker capability probe so callers can discover and plan the diagnostic boundary without executing live broker actions.

#### Scenario: Caller lists broker capability catalog entries
- **WHEN** a caller lists catalog entries with the `broker` or `capability` label
- **THEN** the catalog includes a trade-source entry for the broker capability probe
- **AND** the entry resolves to the stable broker capability trade preset

#### Scenario: Caller plans the broker capability catalog entry
- **WHEN** a caller executes `catalog plan --entry broker-capabilities`
- **THEN** the plan resolves to the trade `broker-capabilities` command
- **AND** the plan includes non-execution provenance and constraints
- **AND** the underlying broker capability probe is not executed
