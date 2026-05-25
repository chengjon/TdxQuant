## Context

`_validate_catalog_registry()` resolves selected catalog entries and already counts matching entries and labels. Resolved entries include normalized `source` values, so source counts can be derived in the same non-executing pass.

## Goals / Non-Goals

- Goal: expose sorted `entry_source_counts` for resolved entries selected by `catalog validate`.
- Goal: project the count map through `catalog validate --view summary`.
- Non-goal: executing entries, validating runtime readiness, changing catalog plan/run behavior, or proving that a source-specific operation is available.

## Decisions

- Count sources after entry resolution and after optional label filtering. This matches `entry_count` and `entry_label_counts`.
- Return an empty object for bundle-only validation. This keeps the field present without implying entry validation happened.
- Reuse resolved entry data rather than raw JSON rows, so validation remains aligned with existing normalization.

## Risks / Trade-offs

- Source counts can be mistaken for runnable capability coverage. Mitigation: FUNCTION_TREE and spec text explicitly mark this as selected-entry structural metadata only.
- The source taxonomy is currently small. Mitigation: sorted map output stays additive if new sources appear later.

## Migration Plan

The field is additive. Existing callers can ignore it. Rollback removes the field and its tests/spec delta.

## Open Questions

None.
