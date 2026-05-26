## Context

`catalog validate --kind bundle --label followup --view summary` already projects `bundle_step_name_counts`, `bundle_step_entry_counts`, `task_report_bundle_step_name_counts`, and `task_report_bundle_step_entry_counts`. Existing summary fields provide source and label key counts; this change extends the same read-only pattern to step name and step entry maps.

## Goals / Non-Goals

**Goals:**

- Derive selected bundle step name/entry key counts from existing summary count maps.
- Derive task+report bundle step name/entry key counts from existing summary count maps.
- Preserve non-execution behavior and existing validation payload semantics.

**Non-Goals:**

- Do not execute catalog entries, reports, tasks, trades, or bundles.
- Do not expose full bundle or step manifests.
- Do not change catalog discovery, bundle resolution, or entry matching.
- Do not claim workflow-builder coverage, broker readiness, execution readiness, or trading safety.

## Decisions

- Add the fields only in `_build_catalog_summary_view()`.
  - Rationale: the source maps are already computed by catalog validation; the summary projection is the smallest stable surface for derived counts.
  - Alternative considered: add the fields to the base validation payload. That would broaden the contract beyond summary view and is not needed for this registry-oriented field.
- Use `len(validation.get("<map>") or {})`.
  - Rationale: this mirrors existing key-count fields and safely handles missing/empty maps.

## Risks / Trade-offs

- Risk: users may confuse key counts with complete step counts.
  - Mitigation: tests and FUNCTION_TREE boundary state that these fields count distinct projected map keys, not resolved step totals or execution coverage.
