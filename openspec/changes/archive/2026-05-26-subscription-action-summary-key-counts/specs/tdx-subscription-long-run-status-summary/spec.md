## ADDED Requirements

### Requirement: Subscription governance action summary SHALL expose action map key counts

Subscription long-run status summaries SHALL include additive `status_summary.governance.action_summary.severity_key_count`, `action_name_key_count`, `reason_source_key_count`, and `reason_code_key_count` fields derived from existing action-summary count maps without changing advisory action generation, governance decisions, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Empty action summary reports zero key counts

- **WHEN** no advisory governance actions exist
- **THEN** `governance.action_summary.severity_key_count` MUST be `0`
- **AND** `governance.action_summary.action_name_key_count` MUST be `0`
- **AND** `governance.action_summary.reason_source_key_count` MUST be `0`
- **AND** `governance.action_summary.reason_code_key_count` MUST be `0`

#### Scenario: Action summary reports count-map key counts

- **WHEN** advisory governance actions produce severity, action-name, reason-source, and reason-code count maps
- **THEN** each action-summary `*_key_count` field MUST equal the number of keys in its corresponding count map
- **AND** existing `governance.action_count`, `governance.action_summary.count`, and action-summary count maps MUST remain available

#### Scenario: Action key counts remain advisory only

- **WHEN** a caller inspects subscription long-run governance status
- **THEN** the action key-count fields MUST NOT expose full actions in compact summary view
- **AND** the fields MUST NOT execute actions or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the fields MUST NOT be treated as health, readiness, PID liveness, process ownership, escalation policy, or governance policy proof

