## Context

`catalog validate --view summary` is a non-executing projection of catalog validation results. It already includes `entry_source_counts` and `entry_label_counts`; this change adds small derived fields so callers can read the number of distinct projected source/label keys without recomputing map lengths.

## Goals / Non-Goals

**Goals:**

- Derive `entry_source_key_count` from `entry_source_counts`.
- Derive `entry_label_key_count` from `entry_label_counts`.
- Preserve the existing non-execution boundary for catalog validation.

**Non-Goals:**

- Do not execute catalog entries, reports, tasks, trades, or bundles.
- Do not expose full entry manifests or label assignment details.
- Do not change catalog discovery, filtering, matching, or label semantics.

## Decisions

- Add the fields only in `_build_catalog_summary_view()`.
  - Rationale: validation already computes and stores the count maps. The summary view is the stable projection layer for derived read-only fields.
  - Alternative considered: mutate the validation payload itself. That would broaden the behavior surface and is unnecessary for a summary-only field.
- Use `len(validation.get("<map>") or {})` for both fields.
  - Rationale: this matches existing key-count projection patterns and keeps missing/empty maps safe.

## Risks / Trade-offs

- Risk: readers may treat key counts as execution coverage.
  - Mitigation: tests and FUNCTION_TREE boundary state that the fields are non-executing and only count projected map keys.
