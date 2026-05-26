## Context

`catalog validate --kind bundle --label followup --view summary` already projects selected bundle and task+report `source:name` / `source:entry` count maps. This change adds map-length fields in the same summary projection layer used by prior catalog key-count fields.

## Goals / Non-Goals

**Goals:**

- Derive selected bundle source-qualified step name/entry key counts from existing summary count maps.
- Derive task+report bundle source-qualified step name/entry key counts from existing summary count maps.
- Preserve non-execution behavior and existing validation semantics.

**Non-Goals:**

- Do not execute catalog entries, reports, tasks, trades, or bundles.
- Do not expose full bundle or step manifests.
- Do not change catalog discovery, bundle resolution, source semantics, or entry matching.
- Do not claim workflow-builder coverage, broker readiness, execution readiness, or trading safety.

## Decisions

- Add the fields only in `_build_catalog_summary_view()`.
  - Rationale: the source maps are already available in validation, and summary view is the intended projection surface for derived read-only fields.
  - Alternative considered: add the fields to the full validation payload. That would broaden the contract beyond this summary-only need.
- Use `len(validation.get("<map>") or {})`.
  - Rationale: this matches existing derived key-count behavior and keeps missing/empty maps safe.

## Risks / Trade-offs

- Risk: source-qualified key counts may be mistaken for complete resolved step totals.
  - Mitigation: tests and FUNCTION_TREE boundary state that these fields only count distinct projected `source:name` / `source:entry` map keys.
