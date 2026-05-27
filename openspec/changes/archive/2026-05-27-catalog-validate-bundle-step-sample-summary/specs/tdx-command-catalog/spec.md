## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose bundle-step sample metadata

Command catalog validation summary views SHALL include additive read-only bounded sample metadata for selected bundles and SHALL mirror that metadata in the compact `bundle_step_summary` object without executing catalog entries, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Validation summary includes selected bundle sample metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary view MUST include bounded `bundle_samples` containing selected bundle names only
- **AND** `bundle_sample_count` MUST equal the length of `bundle_samples`
- **AND** `bundle_sample_limit` and `bundle_sample_truncated` MUST describe the bounded sample projection
- **AND** the summary MUST NOT expose full entry manifests, full bundle manifests, full step manifests, option values, resolved args, or executable instructions
- **AND** the summary MUST NOT execute catalog entries, task commands, report commands, trade commands, provider calls, or bundle steps

#### Scenario: Compact bundle-step summary mirrors sample metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** `bundle_step_summary.sample_count` MUST match `bundle_sample_count`
- **AND** `bundle_step_summary.sample_limit` MUST match `bundle_sample_limit`
- **AND** `bundle_step_summary.sample_truncated` MUST match `bundle_sample_truncated`
- **AND** existing `bundle_step_summary` count and key-count fields MUST remain available
- **AND** existing family-specific summaries MUST remain available and unchanged

#### Scenario: Validation summary handles empty bundle selections deterministically

- **WHEN** a catalog validation summary selection has no matching bundles
- **THEN** `bundle_sample_count` MUST be `0`
- **AND** `bundle_samples` MUST be empty
- **AND** `bundle_step_summary.sample_count` MUST be `0`
- **AND** sample metadata MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
