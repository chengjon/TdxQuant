## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose bundle step summary

Command catalog validation summary views SHALL include additive read-only `bundle_step_summary` metadata derived from existing selected-bundle validation counts and maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Validation summary includes compact selected-bundle step metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label <label> --view summary`
- **THEN** the summary view MUST include `bundle_step_summary.bundle_count` matching `bundle_count`
- **AND** it MUST include `step_count` matching `bundle_step_count`
- **AND** it MUST include label and step-map key counts derived from the corresponding projected count maps
- **AND** existing selected-bundle sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
#### Scenario: Validation summary handles no selected bundles

- **WHEN** a catalog validation summary selection has no selected bundles
- **THEN** `bundle_step_summary.bundle_count` MUST be `0`
- **AND** `step_count` and map key counts MUST be `0`
- **AND** the summary MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
