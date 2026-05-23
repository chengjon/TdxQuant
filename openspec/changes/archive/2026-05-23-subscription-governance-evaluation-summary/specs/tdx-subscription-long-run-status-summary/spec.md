## MODIFIED Requirements

### Requirement: Subscription long-run status summary SHALL expose advisory governance posture

The system SHALL include an advisory `governance` object in `status_summary` that summarizes operator-review posture without changing reconnect, backoff, restart, lifecycle, or event-stream behavior.

#### Scenario: Governance observes healthy or unevaluated state

- **WHEN** no stale input or resilience state requires manual review
- **THEN** `governance.decision` MUST be `observe`
- **AND** `governance.requires_manual_review` MUST be `false`
- **AND** `governance.evaluation_summary` MUST identify not-evaluated components without triggering reconnect, backoff, restart, lifecycle, or event-stream changes

#### Scenario: Governance requests manual review

- **WHEN** explicit stale inputs or resilience state require manual review
- **THEN** `governance.decision` MUST be `manual_review`
- **AND** `governance.requires_manual_review` MUST be `true`
- **AND** `governance.reasons` MUST describe each review reason
- **AND** `governance.evaluation_summary` MUST identify evaluated components and stale components
- **AND** the governance result MUST remain advisory-only

### Requirement: Bridge watch-status CLI SHALL expose summary view

The bridge watch-status CLI SHALL expose an opt-in summary view that projects the existing detailed watch status payload without changing bridge HTTP, worker, reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

#### Scenario: Caller requests bridge watch-status summary view

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the CLI MUST still call the existing bridge watch-status request path
- **AND** the CLI MUST print a compact JSON payload
- **AND** the compact payload MUST include selected runtime identity fields derived from `control` and `watch_status` when present
- **AND** the compact payload MUST include `status_summary.governance.action_summary` when the detailed payload provides it
- **AND** the compact payload MUST include `status_summary.governance.evaluation_summary` when the detailed payload provides it
- **AND** the detailed payload MUST remain the default when no summary view is requested

#### Scenario: Bridge watch-status summary view preserves advisory boundary

- **WHEN** the detailed watch status payload contains governance advisory output
- **THEN** the summary view MUST treat governance fields and runtime identity fields as read-only projection data
- **AND** the summary view MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes
