## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose entry summary

Command catalog validation summary views SHALL include additive read-only `entry_summary` metadata derived from existing selected-entry validation counts and maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Validation summary includes compact selected-entry metadata

- **WHEN** a caller runs `catalog validate --kind entry --label <label> --view summary`
- **THEN** the summary view MUST include `entry_summary.count` matching `entry_count`
- **AND** it MUST include `source_key_count` and `label_key_count` derived from the corresponding projected count maps
- **AND** existing selected-entry sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full entry manifests, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
#### Scenario: Validation summary handles no selected entries

- **WHEN** a catalog validation summary selection has no selected entries
- **THEN** `entry_summary.count` MUST be `0`
- **AND** `source_key_count` and `label_key_count` MUST be `0`
- **AND** the summary MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
