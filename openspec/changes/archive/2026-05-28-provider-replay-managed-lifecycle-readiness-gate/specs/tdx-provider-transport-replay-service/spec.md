## MODIFIED Requirements

### Requirement: Provider replay CLI SHALL expose read-only lifecycle readiness summaries

Provider replay CLI SHALL expose a read-only `lifecycle-readiness` command that summarizes lifecycle control prerequisites without executing lifecycle control.

#### Scenario: Managed lifecycle readiness counts available lifecycle surfaces

- **GIVEN** provider replay config includes `lifecycle_state_file`
- **AND** detailed lifecycle status reports `control_status=operator_opt_in_available`
- **AND** detailed lifecycle supervision reports `supervision_status=operator_opt_in_available`
- **WHEN** lifecycle readiness is built
- **THEN** `lifecycle_controller`, `supervisor_loop`, and `operator_opt_in_control` MUST be counted as satisfied requirements
- **AND** the readiness output MUST remain non-executing.

#### Scenario: Managed lifecycle readiness is ready only when ownership is proven

- **GIVEN** provider replay config includes `lifecycle_state_file`
- **AND** lifecycle readiness includes a valid, non-stale statefile check
- **AND** lifecycle readiness includes ownership diagnostics with `ownership_status=owned`
- **WHEN** lifecycle readiness is built
- **THEN** `ready` MUST be `true`
- **AND** `readiness_status` MUST be `ready`
- **AND** `missing_requirement_count` MUST be `0`
- **AND** `dispatch_executed` MUST remain `false`
- **AND** the command MUST NOT start, stop, restart, supervise, daemonize, write state files, infer ownership from ports, or enable write behavior.

#### Scenario: Unconfigured lifecycle readiness remains blocked

- **GIVEN** provider replay config does not include `lifecycle_state_file`
- **WHEN** lifecycle readiness is built
- **THEN** lifecycle controller, supervisor loop, operator opt-in control, valid statefile, and owned process identity MUST remain missing.
