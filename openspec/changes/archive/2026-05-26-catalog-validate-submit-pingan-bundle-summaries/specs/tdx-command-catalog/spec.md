## ADDED Requirements

### Requirement: Catalog validation summary SHALL expose submit-once and PingAn bundle summaries

Command catalog validation summary views SHALL include additive read-only `submit_once_bundle_summary` and `pingan_bundle_summary` metadata derived from existing submit-once/PingAn bundle validation counts and maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Validation summary includes compact submit-once bundle metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label submit-once --view summary`
- **THEN** the summary view MUST include `submit_once_bundle_summary.count` matching `submit_once_bundle_count`
- **AND** it MUST include `step_count`, `sample_count`, `sample_limit`, and `sample_truncated` derived from the corresponding projected submit-once sibling fields
- **AND** it MUST include label/source/name/entry/option key-count fields derived from the corresponding projected submit-once sibling fields
- **AND** existing submit-once sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full entry manifests, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Validation summary includes compact PingAn bundle metadata

- **WHEN** a caller runs `catalog validate --kind bundle --label pingan --view summary`
- **THEN** the summary view MUST include `pingan_bundle_summary.count` matching `pingan_bundle_count`
- **AND** it MUST include `step_count`, `sample_count`, `sample_limit`, and `sample_truncated` derived from the corresponding projected PingAn sibling fields
- **AND** it MUST include label/source/name/entry/option key-count fields derived from the corresponding projected PingAn sibling fields
- **AND** existing PingAn sibling fields MUST remain available
- **AND** the summary MUST NOT expose option values, resolved args, full entry manifests, full bundle manifests, or full step manifests
- **AND** the summary MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Validation summary handles no submit-once or PingAn bundles

- **WHEN** a catalog validation summary selection has no matching submit-once or PingAn bundles
- **THEN** the corresponding compact summary `count` MUST be `0`
- **AND** `step_count`, sample metadata, and map key counts MUST remain deterministic zero/empty-derived values
- **AND** the summary MUST remain non-executing and MUST NOT be treated as workflow-builder, broker-readiness, trade-safety, or execution-coverage proof
