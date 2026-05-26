# Design: Catalog selected step resolved-arg key counts

## Context

Bundle plan and preview summary views are non-executing projections. The selected step objects already include a reduced `resolved_args` map produced through `_extract_catalog_key_fields`, and the summary has aggregate count maps for step source/name/entry identities.

Adding resolved-argument key count maps gives callers a compact way to see selected input-shape coverage without exposing raw values or changing dispatch behavior.

## Goals / Non-Goals

- Goal: count resolved argument keys across selected bundle plan/preview steps.
- Goal: count source-qualified resolved argument keys using `<source>:<key>`.
- Non-goal: expose full resolved args or hidden raw option values.
- Non-goal: validate argument semantics or prove provider/broker readiness.
- Non-goal: execute catalog entries, tasks, reports, trades, or bundle steps.

## Decisions

- Use the same selected `steps` list used by existing step source/name/entry count maps.
- Count keys from each step's serialized `resolved_args` dict, because that is what the summary view can safely reference at plan/preview time.
- Sort output keys for stable CLI payloads.

## Risks / Trade-offs

- These maps can be confused with raw bundle option-key counts. The field names use `resolved_arg` to make the post-resolution source explicit.

## Migration Plan

No migration required. Existing summary payload fields remain unchanged.

## Open Questions

None.
