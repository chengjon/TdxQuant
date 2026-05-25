## ADDED Requirements

### Requirement: Catalog validation SHALL expose submit-once and PingAn bundle label counts

`catalog validate` SHALL include additive `submit_once_bundle_label_counts` and `pingan_bundle_label_counts` objects derived from selected resolved bundle labels without executing catalog entries, reports, tasks, trade commands, or bundle steps.

#### Scenario: Detailed validation includes subset label counts

- **WHEN** a caller validates catalog bundles
- **THEN** the detailed validation payload MUST include `submit_once_bundle_label_counts`
- **AND** the detailed validation payload MUST include `pingan_bundle_label_counts`
- **AND** both fields MUST count labels from their matching resolved bundle subsets

#### Scenario: Summary view preserves subset label counts

- **WHEN** a caller requests `catalog validate --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_label_counts`
- **AND** the summary view MUST include `pingan_bundle_label_counts`
- **AND** the summary view MUST remain non-executing

#### Scenario: Subset label counts are registry metadata only

- **WHEN** submit-once or PingAn labels are counted
- **THEN** the counts MUST NOT imply task execution, trade execution, broker readiness, or workflow-builder behavior
