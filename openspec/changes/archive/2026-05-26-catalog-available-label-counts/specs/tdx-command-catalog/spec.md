## ADDED Requirements

### Requirement: Catalog list summary SHALL expose available label counts

Catalog list summary views SHALL include read-only `available_entry_label_count` and `available_bundle_label_count` fields derived from their projected available label arrays when those arrays are present, without exposing full execution behavior or executing catalog entries, bundle steps, task/report commands, submit-once flows, broker probes, or trade operations.

#### Scenario: Entry list summary includes available entry label count

- **WHEN** a caller requests `catalog list --kind entry --view summary` and the result includes `available_entry_labels`
- **THEN** the summary result MUST include `available_entry_label_count` equal to the length of `available_entry_labels`
- **AND** `entry_count`, `matched_entry_count`, and `available_entry_labels` MUST remain unchanged
- **AND** the summary MUST NOT execute catalog entries, task/report commands, broker probes, trade operations, or bundle steps

#### Scenario: Bundle list summary includes available bundle label count

- **WHEN** a caller requests `catalog list --kind bundle --view summary` and the result includes `available_bundle_labels`
- **THEN** the summary result MUST include `available_bundle_label_count` equal to the length of `available_bundle_labels`
- **AND** `bundle_count`, `matched_bundle_count`, and `available_bundle_labels` MUST remain unchanged
- **AND** the summary MUST NOT execute catalog entries, bundle steps, task/report commands, broker probes, or trade operations
