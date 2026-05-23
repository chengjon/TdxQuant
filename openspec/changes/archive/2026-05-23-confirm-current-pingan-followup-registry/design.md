## Context

The command catalog has a stable `task-confirm-current` entry and existing Ping An confirm audit report entries. Existing bundles use names like `confirm-pingan-exception-review`, which are usable but do not carry the exact `confirm_current` method identity that D-07 tracks.

This change is a registry/config addition. It does not change `TdxTradeManager`, `TdxTaskManager`, desktop gateway behavior, or report generation.

## Goals / Non-Goals

**Goals:**

- Make Ping An confirm_current follow-up bundles discoverable under method-explicit `confirm-current-pingan-*` names.
- Reuse existing task and report catalog entries.
- Prove `catalog plan` resolves aliases without executing dispatch.
- Keep `FUNCTION_TREE.md` as the single status/evidence/boundary registry.

**Non-Goals:**

- No new desktop confirm primitive.
- No change to order submission, confirmation dialogs, audit report semantics, or arbitrary workflow building.
- No removal or renaming of the existing shorter `confirm-pingan-*` bundle names.

## Decisions

- Add aliases instead of renaming existing bundles.
  - Rationale: existing names may be referenced by users or docs; aliases improve discoverability without breaking compatibility.
- Use the existing `task-confirm-current` entry for the trade step.
  - Rationale: this preserves current execution routing and keeps the new names as catalog-only composition entries.
- Add the `confirm-current` label to the aliases.
  - Rationale: catalog list filters need a stable way to find these method-explicit entries.

## Risks / Trade-offs

- Bundle count increases with aliases.
  - Mitigation: restrict aliases to the three existing Ping An confirm_current audit review outcomes and document them as fixed runtime entries, not a workflow builder.
- Users could infer a new lower-level primitive exists.
  - Mitigation: keep FUNCTION_TREE boundary explicit that `task-confirm-current` uses the existing confirm_current route and does not add a separate desktop primitive.
