## ADDED Requirements

### Requirement: Subscription long-run status summary SHALL expose lifecycle readiness projection

Subscription-watch status summary SHALL include an additive read-only `lifecycle_readiness` projection that summarizes whether existing local evidence is sufficient for manual lifecycle control.

#### Scenario: Detailed status summary includes blocked lifecycle readiness when evidence is missing

- **WHEN** subscription-watch background status is requested
- **AND** restart preflight evidence is missing or not ready
- **THEN** `status_summary.lifecycle_readiness.ready` MUST be `false`
- **AND** `status_summary.lifecycle_readiness.decision` MUST be `blocked`
- **AND** `status_summary.lifecycle_readiness.reason_codes` MUST include a stable reason code for the missing or blocked evidence
- **AND** the projection MUST include a boundary stating that it is read-only and does not execute lifecycle control.

#### Scenario: Detailed status summary includes ready lifecycle readiness when evidence is sufficient

- **WHEN** subscription-watch background status is requested
- **AND** restart preflight is ready
- **AND** statefile ownership indicates an owned active state with matching local PID evidence
- **AND** supervisor daemon evidence does not block control
- **THEN** `status_summary.lifecycle_readiness.ready` MUST be `true`
- **AND** `status_summary.lifecycle_readiness.decision` MUST be `ready`
- **AND** `status_summary.lifecycle_readiness.reason_codes` MUST be empty.

#### Scenario: Summary view preserves lifecycle readiness projection

- **WHEN** bridge watch status is requested with summary view
- **THEN** the HTTP and CLI summary payloads MUST include `status_summary.lifecycle_readiness` when detailed status summary includes it
- **AND** the summary payload MUST NOT expose raw statefile content, owner token, daemon command, daemon settings, raw control payload, or full detailed payload through this projection.

#### Scenario: Lifecycle readiness projection remains read-only

- **WHEN** `status_summary.lifecycle_readiness` is produced
- **THEN** the projection MUST NOT call start, stop, restart, restart preflight, supervisor tick, supervisor run, daemon start, daemon stop, probe, signal, schedule retry, or mutate provider state
- **AND** the projection MUST NOT claim live provider availability, broker readiness, trading readiness, PID ownership beyond existing local evidence, or production lifecycle health.
