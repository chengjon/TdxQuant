# Design: Catalog available label counts

## Context

Catalog list summary views are reduced projections. For label discovery they currently include available label arrays plus selected/matched counts, while omitting full execution behavior.

Downstream automation can derive label counts from those arrays, but explicit count fields align with the registry's current summary conventions and avoid forcing consumers to parse arrays when they only need cardinality.

## Goals / Non-Goals

- Goal: expose `available_entry_label_count` as the length of `available_entry_labels` when projected.
- Goal: expose `available_bundle_label_count` as the length of `available_bundle_labels` when projected.
- Non-goal: expose additional full catalog manifests or option values.
- Non-goal: execute catalog entries, bundle steps, task/report commands, submit-once flows, broker probes, or trade operations.

## Decisions

- Derive counts from the projected available-label arrays in the summary payload.
- Keep the change additive and summary-only.
- Preserve existing `matched_entry_count`, `matched_bundle_count`, `entry_count`, and `bundle_count` semantics.

## Risks / Trade-offs

- The fields are redundant with array lengths, but they make summary consumers simpler and keep the compact view self-describing.

## Migration Plan

No migration required. Existing catalog summary fields remain unchanged.

## Open Questions

None.
