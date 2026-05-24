## ADDED Requirements

### Requirement: Subscription long-run governance SHALL expose advisory action count

The subscription long-run status summary SHALL include additive `governance.action_count` derived from existing advisory governance actions without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Detailed observe governance has zero action count

- **WHEN** a subscription watch status summary has no advisory governance actions
- **THEN** `governance.action_count` MUST be `0`
- **AND** `governance.action_summary.count` MUST also be `0`

#### Scenario: Detailed manual-review governance counts advisory actions

- **WHEN** a subscription watch status summary includes advisory governance actions
- **THEN** `governance.action_count` MUST equal the number of `governance.actions`
- **AND** `governance.action_count` MUST equal `governance.action_summary.count`

#### Scenario: HTTP summary view preserves advisory action count without full actions

- **WHEN** a caller requests bridge watch status with `view=summary`
- **THEN** the HTTP summary result MUST include `governance.action_count`
- **AND** `governance.action_count` MUST equal the detailed advisory action count
- **AND** the HTTP summary result MUST NOT include the full `governance.actions` list

#### Scenario: CLI summary view preserves advisory action count without full actions

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the CLI summary result MUST include `governance.action_count`
- **AND** `governance.action_count` MUST equal the detailed advisory action count
- **AND** the CLI summary result MUST NOT include the full `governance.actions` list
