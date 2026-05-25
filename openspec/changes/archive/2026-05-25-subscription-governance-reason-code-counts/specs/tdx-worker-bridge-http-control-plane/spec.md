# tdx-worker-bridge-http-control-plane Delta

## ADDED Requirements

### Requirement: Worker bridge watch-status summary SHALL preserve governance reason-code counts

The worker bridge watch-status HTTP summary view SHALL preserve `governance.reason_summary.reason_code_counts` when the underlying subscription status summary provides it, without exposing raw `governance.reasons` or `governance.actions` arrays and without changing worker lifecycle behavior.

#### Scenario: HTTP summary view includes compact reason-code counts

- **WHEN** a caller requests worker bridge watch-status with `view=summary`
- **AND** the underlying status summary includes `governance.reason_summary.reason_code_counts`
- **THEN** the HTTP summary result MUST include `governance.reason_summary.reason_code_counts`
- **AND** the HTTP summary result MUST NOT include full `governance.reasons` or `governance.actions`
- **AND** the HTTP summary request MUST remain a read-only projection

