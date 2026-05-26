## ADDED Requirements

### Requirement: Catalog bundle plan summary SHALL expose selected step resolved-arg key counts

The command catalog SHALL include additive read-only `step_resolved_arg_key_counts`, `step_resolved_arg_key_count`, `step_source_resolved_arg_key_counts`, and `step_source_resolved_arg_key_count` fields in bundle `catalog plan` and `catalog preview` summary views, derived only from selected steps' resolved argument maps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Bundle preview summary includes resolved-arg key counts

- **WHEN** a caller executes `catalog preview --bundle <bundle> --view summary`
- **THEN** the summary view MUST include `step_resolved_arg_key_counts` for resolved argument keys present on selected steps
- **AND** the summary view MUST include `step_resolved_arg_key_count` equal to the number of distinct resolved argument keys
- **AND** the summary view MUST include `step_source_resolved_arg_key_counts` using `<source>:<key>` keys
- **AND** the summary view MUST include `step_source_resolved_arg_key_count` equal to the number of distinct source-qualified resolved argument keys
- **AND** the summary view MUST NOT execute catalog entries, tasks, reports, trades, or bundle steps

#### Scenario: Selected step range scopes resolved-arg key counts

- **WHEN** a caller executes `catalog plan --bundle <bundle> --only-step <step> --view summary`
- **THEN** the resolved-arg key count maps MUST be derived only from the selected step range
- **AND** the maps MUST not count unselected bundle steps
- **AND** existing non-execution provenance, constraints, step source/name/entry count maps, and reduced step projection behavior MUST remain unchanged
