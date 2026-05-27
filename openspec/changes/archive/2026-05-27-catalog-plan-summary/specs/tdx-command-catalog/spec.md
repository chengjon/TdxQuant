## ADDED Requirements

### Requirement: Catalog plan summary SHALL expose planning summary metadata

Command catalog plan and preview summary views SHALL include additive read-only `plan_summary` metadata derived from already projected `plan_outcome`, `selected_step_summary`, and selected-step sibling fields without executing catalog entries, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Plan summary includes selected bundle planning status

- **WHEN** a caller runs `catalog plan --bundle confirm-complete-review --view summary`
- **THEN** the summary view MUST include `plan_summary.mode` equal to `plan`
- **AND** `plan_summary.target_type`, `target_name`, execution mode, ok/code, non-execution, and dispatch execution fields MUST mirror `plan_outcome`
- **AND** `plan_summary.selected_step_count`, selected step range, and key-count fields MUST mirror `selected_step_summary`
- **AND** `plan_summary.has_steps` and `has_step_slice` MUST mirror selected step summary booleans
- **AND** existing `plan_outcome`, `selected_step_summary`, and sibling fields MUST remain available
- **AND** the summary MUST NOT expose full entry manifests, full bundle manifests, full step manifests beyond the existing reduced summary view, option values, raw resolved args, or executable instructions
- **AND** the summary MUST NOT execute catalog entries, task commands, report commands, trade commands, provider calls, or bundle steps

#### Scenario: Preview summary exposes the same planning summary boundary

- **WHEN** a caller runs `catalog preview --bundle confirm-complete-review --view summary`
- **THEN** the summary view MUST include `plan_summary.mode` equal to `preview`
- **AND** `plan_summary.non_execution` MUST be `true`
- **AND** `plan_summary.dispatch_executed` MUST be `false`
- **AND** plan summary metadata MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
