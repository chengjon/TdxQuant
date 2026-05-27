## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose catalog summary metadata

Command catalog validation summary views SHALL include additive read-only `catalog_summary` metadata derived from already projected validation outcome, entry, bundle, label, and source summary fields without executing catalog entries, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Validation summary includes top-level bundle registry status

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary view MUST include `catalog_summary.mode` equal to `validate`
- **AND** `catalog_summary.kind`, selected filters, validity, invalid count, and non-execution marker MUST mirror existing summary fields
- **AND** `catalog_summary.entry_count`, `bundle_count`, and `bundle_step_count` MUST mirror existing compact summary counts
- **AND** `catalog_summary.label_key_count` and `source_key_count` MUST be derived from the compact label and source summaries
- **AND** `catalog_summary.has_bundles`, `has_entries`, `has_invalid_entries`, and `has_selected_label` MUST be deterministic booleans derived from already projected metadata
- **AND** existing compact summary objects and sibling fields MUST remain available
- **AND** the summary MUST NOT expose full entry manifests, full bundle manifests, full step manifests, option values, resolved args, or executable instructions
- **AND** the summary MUST NOT execute catalog entries, task commands, report commands, trade commands, provider calls, or bundle steps

#### Scenario: Validation summary handles empty bundle selections deterministically

- **WHEN** a caller runs `catalog validate --kind bundle --label no-such-label --view summary`
- **THEN** `catalog_summary.bundle_count` MUST be `0`
- **AND** `catalog_summary.bundle_step_count` MUST be `0`
- **AND** `catalog_summary.has_bundles` MUST be `false`
- **AND** `catalog_summary.has_selected_label` MUST be `false`
- **AND** catalog summary metadata MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
