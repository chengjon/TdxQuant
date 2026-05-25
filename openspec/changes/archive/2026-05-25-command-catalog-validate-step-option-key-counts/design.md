## Context

`_validate_catalog_registry()` already resolves selected bundles and walks each resolved step to aggregate source, name, entry, source/name, label, sample, and task/report subset counts. Resolved steps preserve `options` dictionaries, so option-key counts can be derived in the same non-executing traversal.

## Goals / Non-Goals

- Goal: expose sorted `bundle_step_option_key_counts` for all selected resolved bundle steps.
- Goal: expose sorted `task_report_bundle_step_option_key_counts` for selected bundles containing both task and report steps.
- Goal: project both maps through `catalog validate --view summary`.
- Non-goal: validating option values, executing bundle steps, adding arbitrary workflow building, or changing catalog plan/run behavior.

## Decisions

- Count option keys only when `step.options` is a dictionary. This matches the existing catalog schema and avoids interpreting non-object payloads.
- Count keys rather than values. Keys are enough to reveal the preset option surface without exposing larger payloads or turning validation into execution simulation.
- Reuse the existing selected-bundle and task/report subset loops. This keeps behavior aligned with existing count maps and label filters.

## Risks / Trade-offs

- The current runtime bundle set uses few option keys. Mitigation: the field is additive and still useful as the bundle set grows.
- Option-key counts do not prove option values are semantically valid. Mitigation: document the field as a structural, non-executing registry rollup only.

## Migration Plan

The new fields are additive. Existing callers ignore unknown keys. Rollback removes the fields and related tests/spec delta.

## Open Questions

None.
