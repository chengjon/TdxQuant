## Context

The catalog validation summary view is intentionally a registry parser and counter. It already contains detailed count maps and compact per-family summaries for entries, bundle steps, task/report bundles, submit-once bundles, and PingAn bundles. The remaining ergonomics gap is an outcome-level object that identifies the selected validation scope and result without requiring clients to read many sibling fields.

## Design

When `_build_catalog_summary_view()` handles a `validate` result, add `summary["validation_outcome"]` with:

- `kind`
- `selected_label`
- `entry_count`
- `bundle_count`
- `invalid_count`
- `valid`
- `non_execution`
- `ok`
- `code`
- `message`
- `has_invalid_entries`
- `has_selected_label`

The boolean fields are derived from existing scalar fields. The object must not include raw entries, raw bundle definitions, resolved step payloads, or execution outputs.

## Non-Goals

- Do not change catalog validation behavior or registry loading rules.
- Do not execute entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.
- Do not introduce a dynamic workflow builder or claim arbitrary combinations are supported.
