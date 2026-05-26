## Context

`catalog validate --kind bundle --label followup --view summary` already projects selected bundle and task+report option-key count maps. Submit-once/PingAn subset summaries already expose analogous option-key key-count fields. This change adds the same read-only derived fields for the broader selected bundle and task+report projections.

## Goals / Non-Goals

**Goals:**

- Derive selected bundle option-key and source-option-key key counts from existing summary count maps.
- Derive task+report bundle option-key and source-option-key key counts from existing summary count maps.
- Preserve non-execution behavior and existing validation semantics.

**Non-Goals:**

- Do not expose option values.
- Do not validate option semantics or option compatibility.
- Do not execute catalog entries, reports, tasks, trades, or bundles.
- Do not claim workflow-builder coverage, broker readiness, execution readiness, or trading safety.

## Decisions

- Add the fields only in `_build_catalog_summary_view()`.
  - Rationale: the source maps are already available in validation, and the summary projection is the established surface for derived counts.
  - Alternative considered: add the fields to the full validation payload. That would broaden the contract beyond this summary-only need.
- Use `len(validation.get("<map>") or {})`.
  - Rationale: this mirrors existing option-key key-count fields and handles missing/empty maps safely.

## Risks / Trade-offs

- Risk: option-key counts may be mistaken for option semantic validation or value exposure.
  - Mitigation: tests and FUNCTION_TREE boundary state that these fields only count projected map keys and never expose option values or validate semantics.
