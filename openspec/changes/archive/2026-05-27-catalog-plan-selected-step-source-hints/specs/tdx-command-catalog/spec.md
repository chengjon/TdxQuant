## ADDED Requirements

### Requirement: Catalog bundle plan selected-step summary SHALL expose source hints

Catalog bundle plan summary views SHALL include additive read-only `selected_step_summary.first_step_source` and `selected_step_summary.last_step_source` fields derived from existing selected step dispatch source metadata.

#### Scenario: Selected-step summary includes first and last source hints

- **WHEN** a caller runs `catalog plan --bundle <bundle> --view summary`
- **THEN** `selected_step_summary.first_step_source` MUST match the first selected step dispatch source
- **AND** `selected_step_summary.last_step_source` MUST match the last selected step dispatch source
- **AND** the fields MUST be scoped to the selected bundle step slice

#### Scenario: Selected-step source hints remain non-executing

- **WHEN** selected-step summary exposes source hints
- **THEN** the summary MUST NOT expose full dispatch manifests, resolved argument values, full step manifests, full bundle manifests, or execution results
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the summary MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
