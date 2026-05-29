## ADDED Requirements

### Requirement: Subscription watch-status diagnostics SHALL expose lifecycle readiness projection

Subscription watch-status diagnostics SHALL include an additive read-only `diagnostics.lifecycle_readiness` projection when the summary payload provides `status_summary.lifecycle_readiness`.

#### Scenario: CLI diagnostics view projects lifecycle readiness

- **WHEN** a caller runs `bridge watch-status --view diagnostics`
- **AND** the detailed status summary includes `status_summary.lifecycle_readiness`
- **THEN** the diagnostics payload MUST include `diagnostics.lifecycle_readiness`
- **AND** the diagnostics projection MUST preserve `ready`, `decision`, `reason_codes`, selected input status fields, and `boundary`
- **AND** the command MUST NOT call restart preflight, start, stop, restart, supervisor tick, supervisor run, daemon control, probe, signal processes, schedule retry, or mutate provider state.

#### Scenario: HTTP diagnostics view projects lifecycle readiness

- **WHEN** a caller requests `GET /bridge/v1/watch/status?view=diagnostics`
- **AND** the detailed status summary includes `status_summary.lifecycle_readiness`
- **THEN** the HTTP diagnostics payload MUST include `diagnostics.lifecycle_readiness`
- **AND** the diagnostics projection MUST NOT expose raw statefile content, owner token, daemon command, daemon settings, raw control payload, or full detailed payload.

#### Scenario: Diagnostics lifecycle readiness remains read-only

- **WHEN** `diagnostics.lifecycle_readiness` is produced
- **THEN** it MUST be derived from existing summary data
- **AND** it MUST NOT prove live provider availability, broker readiness, trading readiness, PID ownership beyond existing local evidence, or production lifecycle health.
