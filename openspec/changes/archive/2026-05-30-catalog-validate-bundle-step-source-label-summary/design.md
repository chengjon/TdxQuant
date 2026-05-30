## Context

`catalog validate --kind bundle --label <label> --view summary` already exposes bundle step counts by source, name, entry, source-name, source-entry, option key, and source-option key. It also exposes bundle label counts. E-11 now needs one more read-only projection that joins a step's source with each parent bundle label, allowing a stable summary of task/report step coverage per label.

## Goals / Non-Goals

**Goals:**

- Add deterministic `source:label` counts for bundle steps in validation output.
- Include the same projection for the task/report bundle subset used by E-11.
- Keep summary output compact and non-executing.
- Register the evidence in `FUNCTION_TREE.md` without changing E-11 status to implemented.

**Non-Goals:**

- Do not execute task, report, trade, or bundle steps.
- Do not add `catalog run` behavior.
- Do not build arbitrary workflow composition.
- Do not claim task/report combos are production-ready workflows.

## Decisions

- Count each selected bundle step once for each label on its parent bundle using key format `<source>:<label>`, for example `task:followup` and `report:followup`.
- Expose fields both in raw validation data and summary view:
  - `bundle_step_source_label_counts`
  - `bundle_step_source_label_key_count`
  - `task_report_bundle_step_source_label_counts`
  - `task_report_bundle_step_source_label_key_count`
- Add matching key-counts to `bundle_step_summary` and `task_report_bundle_summary`.

## Risks / Trade-offs

- Counts can exceed `bundle_step_count` when a bundle has multiple labels because each source-label pair is counted. Tests should assert selected-label pairs where useful, not assume all source-label counts sum to step count.
- The new fields are descriptive catalog metadata; consumers must not treat them as execution readiness.
