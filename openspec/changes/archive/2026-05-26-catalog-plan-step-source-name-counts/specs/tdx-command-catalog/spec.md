# tdx-command-catalog Spec Delta

## ADDED Requirements

### Requirement: Command catalog plan and preview summary SHALL expose step source-name counts

Command catalog bundle plan and preview summary views SHALL include additive read-only `step_source_name_counts` and `step_source_name_key_count` fields derived from selected resolved bundle step `source:name` pairs without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Caller plans a mixed bundle summary

- **WHEN** a caller executes `catalog plan --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_source_name_counts` for selected resolved step `source:name` pairs
- **AND** the summary view MUST include `step_source_name_key_count` equal to the number of keys in `step_source_name_counts`
- **AND** `selected_step_count` MUST remain the selected resolved step total

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary` with step filtering
- **THEN** the summary view MUST include `step_source_name_counts` for the selected filtered steps
- **AND** `step_source_name_key_count` MUST equal the number of keys in that filtered `step_source_name_counts` map

#### Scenario: Step source-name counts remain non-executing

- **WHEN** a caller inspects a catalog plan or preview summary
- **THEN** `step_source_name_counts` and `step_source_name_key_count` MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the fields MUST NOT be treated as a complete step manifest, workflow execution coverage, provider readiness, broker readiness, or trade safety proof
