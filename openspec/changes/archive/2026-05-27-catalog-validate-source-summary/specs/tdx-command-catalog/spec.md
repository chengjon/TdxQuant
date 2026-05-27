## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose source summary metadata

Command catalog validation summary views SHALL include additive read-only `source_summary` metadata derived from already projected entry and bundle-step source count maps without executing catalog entries, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Validation summary includes bundle-step source coverage

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary view MUST include `source_summary.bundle_step_key_count` matching `bundle_step_source_key_count`
- **AND** `source_summary.entry_key_count` MUST match `entry_source_key_count`
- **AND** `source_summary.total_key_count` MUST count distinct keys across projected entry and bundle-step source maps
- **AND** `source_summary.bundle_step_count` MUST match `bundle_step_count`
- **AND** `source_summary.entry_count` MUST match `entry_count`
- **AND** the summary MUST NOT expose full entry manifests, full bundle manifests, full step manifests, option values, resolved args, or executable instructions
- **AND** the summary MUST NOT execute catalog entries, task commands, report commands, trade commands, provider calls, or bundle steps

#### Scenario: Validation summary includes entry source coverage

- **WHEN** a caller runs `catalog validate --kind entry --label report --view summary`
- **THEN** `source_summary.entry_key_count` MUST match `entry_source_key_count`
- **AND** `source_summary.bundle_step_key_count` MUST match `bundle_step_source_key_count`
- **AND** `source_summary.has_entry_sources` MUST reflect whether projected entry source counts are non-empty
- **AND** `source_summary.has_bundle_step_sources` MUST reflect whether projected bundle-step source counts are non-empty
- **AND** source summary metadata MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
