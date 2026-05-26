## ADDED Requirements

### Requirement: Command catalog plan and preview summary SHALL expose step entry counts

Command catalog bundle plan and preview summary views SHALL include additive read-only `step_entry_counts` and `step_entry_key_count` fields derived from selected resolved bundle steps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Caller plans a mixed bundle summary

- **WHEN** a caller executes `catalog plan --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_entry_counts` for selected resolved step entries
- **AND** the summary view MUST include `step_entry_key_count` equal to the number of keys in `step_entry_counts`
- **AND** `selected_step_count` MUST remain the selected resolved step total

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary` with step filtering
- **THEN** the summary view MUST include `step_entry_counts` for the selected filtered steps
- **AND** `step_entry_key_count` MUST equal the number of keys in that filtered `step_entry_counts` map

#### Scenario: Step entry counts remain non-executing

- **WHEN** a caller inspects a catalog plan or preview summary
- **THEN** `step_entry_counts` and `step_entry_key_count` MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps
- **AND** the fields MUST NOT be treated as a complete step manifest, workflow execution coverage, provider readiness, broker readiness, or trade safety proof

