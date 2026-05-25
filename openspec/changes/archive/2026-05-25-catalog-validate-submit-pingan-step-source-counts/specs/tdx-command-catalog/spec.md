## ADDED Requirements

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle step-source counts

`catalog validate` SHALL include additive `submit_once_bundle_step_source_counts` and `pingan_bundle_step_source_counts` objects derived from selected resolved bundle step sources without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset step-source counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_step_source_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_step_source_counts`
- **AND** both fields MUST count resolved step sources from their matching bundle subsets

#### Scenario: Summary view preserves subset step-source counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_step_source_counts`
- **AND** the summary view MUST include `pingan_bundle_step_source_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset step-source counts are registry metadata only

- **WHEN** submit-once or PingAn resolved step sources are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, or workflow-builder behavior
