## Overview

Add an additive `task_report_bundle_label_counts` object to catalog validation payloads. The field is computed only from bundles that resolve successfully and contain both task and report steps.

## Data Shape

`task_report_bundle_label_counts` is a deterministic JSON object mapping bundle label to count.

- Counts are incremented once per task+report bundle per label.
- Keys are sorted before output.
- Empty matches produce `{}`.

`catalog validate --view summary` copies the object into `summary_view` so reduced views can audit fixed combination label distribution without exposing complete bundle definitions.

## Boundary

The field is a structural validation rollup only. It does not execute tasks, reports, trades, bundle steps, or workflow logic; it is not a complete bundle listing and not a workflow builder.
