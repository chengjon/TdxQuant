## Design

Entry planning should accept the top-level `--side` override because there is a single target entry. Bundle planning is different: each step resolves through its own entry, preset, and optional step options. A top-level `--side` should not override a side-specific bundle step.

The bundle step namespace builder will drop top-level `side` before applying step options and resolving the step preset. This preserves any explicit step option side and lets the step preset's side remain authoritative.

## Boundaries

- This is non-executing bundle planning metadata only.
- It must not execute submit-once, task, report, bundle, provider, buy/sell, submit-ready, or confirm-current workflows.
- It does not remove entry-level plan/preview `--side` override behavior.
- It does not add side override support to `catalog run`.

