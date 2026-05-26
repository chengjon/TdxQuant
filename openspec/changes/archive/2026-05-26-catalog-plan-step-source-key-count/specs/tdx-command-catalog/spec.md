## ADDED Requirements

### Requirement: Command catalog plan and preview summary SHALL expose step source key count

Command catalog bundle plan and preview summary views SHALL include additive read-only `step_source_key_count` derived from the existing `step_source_counts` map for selected resolved bundle steps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Caller plans a mixed bundle summary

- **WHEN** a caller executes `catalog plan --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_source_counts`
- **AND** the summary view MUST include `step_source_key_count` equal to the number of keys in `step_source_counts`
- **AND** `step_source_key_count` MUST count distinct selected step sources, not selected steps

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary` with step filtering
- **THEN** the summary view MUST include `step_source_counts` for the selected filtered steps
- **AND** `step_source_key_count` MUST equal the number of keys in that filtered `step_source_counts` map

#### Scenario: Step source key count remains non-executing

- **WHEN** a caller inspects a catalog plan or preview summary
- **THEN** `step_source_key_count` MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the field MUST NOT be treated as workflow execution coverage, provider readiness, broker readiness, or trade safety proof

