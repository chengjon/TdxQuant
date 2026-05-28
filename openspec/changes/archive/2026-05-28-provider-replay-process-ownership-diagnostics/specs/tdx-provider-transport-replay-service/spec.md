## ADDED Requirements

### Requirement: Provider replay daemon status SHALL expose process ownership diagnostics

Provider replay daemon status SHALL expose a read-only process ownership diagnostic that combines statefile validity, owner token, config hash, PID liveness, and optional process identity match.

#### Scenario: Owned process is reported when all ownership checks pass

- **WHEN** statefile diagnostics are valid, provider id matches, config hash matches, owner token matches when expected, PID is live, and optional process identity matches
- **THEN** ownership diagnostics MUST report `ownership_status=owned`
- **AND** `owned_process` MUST be `true`
- **AND** daemon status `control_allowed` MAY be true for the managed replay daemon

#### Scenario: Process ownership diagnostics explain missing ownership

- **WHEN** the PID is not live, owner token mismatches, config hash mismatches, statefile is stale, or optional process identity mismatches
- **THEN** ownership diagnostics MUST report a specific non-owned status
- **AND** `owned_process` MUST be `false`
- **AND** diagnostics MUST remain read-only

#### Scenario: Lifecycle readiness can count owned process identity

- **WHEN** lifecycle readiness includes ownership diagnostics proving `owned_process=true`
- **THEN** `owned_process_identity` MUST move from missing requirements to satisfied requirements
- **AND** readiness MUST remain blocked until the remaining lifecycle requirements are satisfied

#### Scenario: Ownership diagnostics remain bounded

- **WHEN** ownership diagnostics are available
- **THEN** the implementation MUST NOT kill processes, infer ownership from ports, enable default command-line inspection, recover real providers, or assert broker/workflow/write readiness

