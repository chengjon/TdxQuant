# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog validate SHALL summarize task/report bundle step sources

The command catalog validation workflow SHALL expose compact aggregate source counts for selected task/report bundles, derived from resolved catalog metadata without executing catalog dispatch.

#### Scenario: Caller validates follow-up bundles with source counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_source_counts`
- **AND** the counts MUST aggregate resolved step sources only for bundles whose resolved steps include both `task` and `report`
- **AND** the counts MUST include task and report sources when matching task/report bundles exist
- **AND** the validation MUST NOT execute any selected task, report, trade, or bundle step

#### Scenario: Caller validates follow-up bundles with summary source counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_source_counts`
- **AND** the summary payload MUST retain `non_execution=true`
- **AND** the summary payload MUST NOT include full entry or bundle detail rows
