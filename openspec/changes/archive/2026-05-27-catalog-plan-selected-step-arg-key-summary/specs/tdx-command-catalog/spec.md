## ADDED Requirements

### Requirement: Catalog bundle plan selected-step summary SHALL expose resolved-arg key counts

Catalog bundle plan summary views SHALL include additive read-only `selected_step_summary.step_resolved_arg_key_count` and `selected_step_summary.step_source_resolved_arg_key_count` fields derived from the existing selected-step resolved-arg key count metadata.

#### Scenario: Selected-step summary includes resolved-arg key counts

- **WHEN** a caller runs `catalog plan --bundle <bundle> --view summary`
- **THEN** `selected_step_summary.step_resolved_arg_key_count` MUST match top-level `step_resolved_arg_key_count`
- **AND** `selected_step_summary.step_source_resolved_arg_key_count` MUST match top-level `step_source_resolved_arg_key_count`
- **AND** the fields MUST be scoped to the selected bundle step slice

#### Scenario: Selected-step resolved-arg key counts remain non-executing

- **WHEN** selected-step summary exposes resolved-arg key counts
- **THEN** the summary MUST NOT expose resolved argument values, full step manifests, full bundle manifests, or execution results
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the summary MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
