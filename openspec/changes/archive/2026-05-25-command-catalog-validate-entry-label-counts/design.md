## Context

`_validate_catalog_registry()` already resolves selected entries to confirm catalog structure and applies optional label filters. The resolved entry includes a normalized `labels` list, so entry label counts can be derived in the same non-executing validation pass.

## Goals / Non-Goals

- Goal: expose sorted `entry_label_counts` for resolved entries selected by `catalog validate`.
- Goal: preserve the existing label filter behavior and entry count semantics.
- Goal: project the count map through `catalog validate --view summary`.
- Non-goal: listing complete entry rows in summary view, executing entries, validating runtime readiness, or changing catalog run/plan behavior.

## Decisions

- Count labels after entry resolution and after the optional label filter. This matches the existing selected-entry count surface.
- Return an empty object when no entries are selected or when validation is bundle-only. This keeps the field present without implying missing entry work was performed.
- Do not count labels directly from raw JSON. Resolved entries already normalize labels and should remain the validation source.

## Risks / Trade-offs

- Label counts may be mistaken for execution coverage. Mitigation: document the field as structural, selected-entry validation metadata only.
- Entry label counts overlap with `catalog list` label discovery. Mitigation: validation counts selected resolved entries, while list discovery is a discovery surface.

## Migration Plan

The field is additive. Existing callers that ignore unknown keys continue working. Rollback removes the field and its tests/spec delta.

## Open Questions

None.
