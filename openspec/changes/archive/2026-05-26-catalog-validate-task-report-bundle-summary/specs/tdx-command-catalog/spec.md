## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose task/report bundle summary

Command catalog validation summary views SHALL include additive read-only `task_report_bundle_summary` metadata derived from existing task/report bundle validation counts and maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Validation summary includes compact task/report bundle metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label <label> --view summary`
- **THEN** the summary view MUST include `task_report_bundle_summary.count` matching `task_report_bundle_count`
- **AND** it MUST include `step_count`, `sample_count`, `sample_limit`, and `sample_truncated` matching the existing task/report bundle sibling fields
- **AND** it MUST include label and step-map key counts derived from the corresponding projected count maps
- **AND** existing task/report bundle sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
#### Scenario: Validation summary handles no task/report bundles

- **WHEN** a catalog validation summary selection has no task/report bundles
- **THEN** `task_report_bundle_summary.count` MUST be `0`
- **AND** sample and map key counts MUST be `0`
- **AND** `sample_truncated` MUST be falsey or `false`
- **AND** the summary MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
