# Design: Subscription action summary key counts

## Context

`governance.action_summary` is derived from advisory governance actions. It currently contains primary action metadata and four count maps:

- `severity_counts`
- `action_name_counts`
- `reason_source_counts`
- `reason_code_counts`

The new key-count fields are cardinality hints for these maps. They do not alter action construction and do not make actions executable.

## Goals / Non-Goals

- Goal: expose `severity_key_count` as `len(severity_counts)`.
- Goal: expose `action_name_key_count` as `len(action_name_counts)`.
- Goal: expose `reason_source_key_count` as `len(reason_source_counts)`.
- Goal: expose `reason_code_key_count` as `len(reason_code_counts)`.
- Goal: return zero key counts when no advisory actions exist.
- Non-goal: change advisory action names, reasons, severity, or descriptions.
- Non-goal: treat advisory actions as an execution queue, escalation policy, lifecycle controller, or broker/provider command.

## Decisions

- Derive key counts in `_build_subscription_watch_governance_action_summary()` from the same dictionaries used to build the public count maps.
- Keep the fields under `action_summary`, not top-level governance, because they describe the shape of existing action rollups.
- Preserve the existing compatibility field `severity`.

## Risks / Trade-offs

- Key counts can be mistaken for action counts. Keeping `action_count` and `action_summary.count` unchanged and naming these fields `*_key_count` preserves the distinction.

## Migration Plan

No migration required. Existing summary fields remain unchanged.

## Open Questions

None.

