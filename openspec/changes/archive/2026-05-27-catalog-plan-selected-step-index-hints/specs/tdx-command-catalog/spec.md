## ADDED Requirements

### Requirement: Catalog bundle plan selected-step summary SHALL expose index hints

Catalog bundle plan summary views SHALL include additive read-only `selected_step_summary.first_step_index` and `selected_step_summary.last_step_index` fields derived from existing selected step index metadata.

#### Scenario: Selected-step summary includes first and last index hints

- **WHEN** a caller runs `catalog plan --bundle <bundle> --view summary`
- **THEN** `selected_step_summary.first_step_index` MUST match the first selected step index
- **AND** `selected_step_summary.last_step_index` MUST match the last selected step index
- **AND** the fields MUST be scoped to the selected bundle step slice

#### Scenario: Selected-step index hints remain non-executing

- **WHEN** selected-step summary exposes index hints
- **THEN** the summary MUST NOT expose full step manifests, full dispatch manifests, resolved argument values, full bundle manifests, or execution results
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the summary MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
