## ADDED Requirements

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle step-entry counts

`catalog validate` SHALL include additive `submit_once_bundle_step_entry_counts` and `pingan_bundle_step_entry_counts` objects derived from selected resolved bundle step entries without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset step-entry counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_step_entry_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_step_entry_counts`
- **AND** both fields MUST count resolved step entries from their matching bundle subsets

#### Scenario: Summary view preserves subset step-entry counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_step_entry_counts`
- **AND** the summary view MUST include `pingan_bundle_step_entry_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset step-entry counts are registry metadata only

- **WHEN** submit-once or PingAn resolved step entries are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, workflow-builder behavior, complete execution-chain coverage, or a full step manifest
