# tdx-provider-transport-replay-service Delta

## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose not-requested targets

Provider replay status SHALL include an additive `runtime.probe_summary.not_requested` list identifying probe targets whose normalized status is `not_requested`, without starting sockets, executing unrequested probes, or managing daemon lifecycle.

#### Scenario: No probes requested lists every target

- **WHEN** provider replay status is built without explicit probe results
- **THEN** `runtime.probe_summary.not_requested` MUST contain every supported probe target in stable order
- **AND** `runtime.probe_summary.requested_count` MUST remain `0`
- **AND** the status MUST remain read-only

#### Scenario: Partial probes list skipped targets

- **WHEN** provider replay status is built with only a subset of explicit probe results
- **THEN** `runtime.probe_summary.not_requested` MUST list only the targets that were not requested
- **AND** `runtime.probe_summary.requested` MUST list the requested targets
- **AND** probe status counts MUST remain derived from normalized probe statuses

#### Scenario: CLI summary preserves not-requested targets

- **WHEN** `provider-replay status --view summary` is requested
- **THEN** `summary_view.probe_summary.not_requested` MUST preserve the detailed probe summary list
- **AND** the summary view MUST remain a read-only projection
