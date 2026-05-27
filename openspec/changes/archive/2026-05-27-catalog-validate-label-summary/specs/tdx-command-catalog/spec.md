## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose label summary metadata

Command catalog validation summary views SHALL include additive read-only `label_summary` metadata derived from already projected entry and bundle label count maps without executing catalog entries, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Validation summary includes selected-label bundle coverage

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary view MUST include `label_summary.selected_label` matching `selected_label`
- **AND** `label_summary.bundle_key_count` MUST match `bundle_label_key_count`
- **AND** `label_summary.entry_key_count` MUST match `entry_label_key_count`
- **AND** `label_summary.selected_bundle_count` MUST match the selected label count in `bundle_label_counts`
- **AND** `label_summary.selected_entry_count` MUST match the selected label count in `entry_label_counts`
- **AND** `label_summary.selected_total_count` MUST equal selected entry plus selected bundle counts
- **AND** `label_summary.total_key_count` MUST count distinct keys across projected entry and bundle label maps
- **AND** the summary MUST NOT expose full entry manifests, full bundle manifests, full step manifests, option values, resolved args, or executable instructions
- **AND** the summary MUST NOT execute catalog entries, task commands, report commands, trade commands, provider calls, or bundle steps

#### Scenario: Validation summary handles selections without matching labels

- **WHEN** a caller runs `catalog validate --kind bundle --label no-such-label --view summary`
- **THEN** `label_summary.selected_label` MUST match the requested label
- **AND** selected entry, selected bundle, and selected total counts MUST be `0`
- **AND** `label_summary.has_selected_label` MUST be `false`
- **AND** label summary metadata MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
