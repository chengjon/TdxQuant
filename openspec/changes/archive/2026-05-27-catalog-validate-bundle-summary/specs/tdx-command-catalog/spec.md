## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose bundle summary metadata

Command catalog validation summary views SHALL include additive read-only `bundle_summary` metadata derived from already projected bundle count, sample, label, and step-count fields without executing catalog entries, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Validation summary includes selected bundle-label coverage

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary view MUST include `bundle_summary.count` matching `bundle_count`
- **AND** `bundle_summary.step_count` MUST match `bundle_step_count`
- **AND** `bundle_summary.sample_count`, `sample_limit`, and `sample_truncated` MUST mirror the bounded bundle sample metadata
- **AND** `bundle_summary.label_key_count` MUST match `bundle_label_key_count`
- **AND** `bundle_summary.has_bundles` MUST reflect whether selected bundle count is non-zero
- **AND** existing `bundle_step_summary` and sibling fields MUST remain available
- **AND** the summary MUST NOT expose full entry manifests, full bundle manifests, full step manifests, option values, resolved args, or executable instructions
- **AND** the summary MUST NOT execute catalog entries, task commands, report commands, trade commands, provider calls, or bundle steps

#### Scenario: Validation summary handles empty bundle selections deterministically

- **WHEN** a caller runs `catalog validate --kind bundle --label no-such-label --view summary`
- **THEN** `bundle_summary.count` MUST be `0`
- **AND** `bundle_summary.step_count` MUST be `0`
- **AND** `bundle_summary.sample_count` MUST be `0`
- **AND** `bundle_summary.has_bundles` MUST be `false`
- **AND** bundle summary metadata MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
