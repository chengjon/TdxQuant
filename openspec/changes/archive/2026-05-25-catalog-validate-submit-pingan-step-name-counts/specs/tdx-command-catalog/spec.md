## ADDED Requirements

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle step-name counts

`catalog validate` SHALL include additive `submit_once_bundle_step_name_counts` and `pingan_bundle_step_name_counts` objects derived from selected resolved bundle step names without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset step-name counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_step_name_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_step_name_counts`
- **AND** both fields MUST count resolved step names from their matching bundle subsets

#### Scenario: Summary view preserves subset step-name counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_step_name_counts`
- **AND** the summary view MUST include `pingan_bundle_step_name_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset step-name counts are registry metadata only

- **WHEN** submit-once or PingAn resolved step names are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, workflow-builder behavior, or complete execution-chain coverage
