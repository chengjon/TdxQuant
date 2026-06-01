## Context

`TdxTaskManager` is the stable facade for scenario tasks, task presets, report workflows, block watchlist tasks, subscription watch tasks, and trade-oriented orchestration. This broad surface is useful to callers but makes the implementation class a hotspot: read-only aggregation/report methods live beside desktop trade write paths and broker lifecycle workflows.

This change introduces a read-only task boundary behind the existing facade. The facade remains the public entrypoint; the new boundary owns selected non-mutating task workflows.

## Goals / Non-Goals

**Goals:**

- Add a dedicated boundary for read-only task workflows.
- Preserve existing `TdxTaskManager` public method names, arguments, result envelope shape, task metadata, and CLI behavior.
- Start with a narrow tracer slice that can be verified through public task-manager behavior.
- Keep the boundary safe for workflows that read/aggregate/validate/plan/export local or provider-backed data without triggering desktop trade execution.

**Non-Goals:**

- No change to task preset JSON schemas.
- No change to report CLI command names.
- No desktop trade buy/sell/submit/confirm implementation move.
- No broker lifecycle, restart/backoff, owner lock, or provider mutation change.
- No workflow-builder semantics.

## Decisions

1. Keep `TdxTaskManager` as a facade.

   Rationale: callers and CLI dispatch already depend on this class. The architecture issue is implementation locality, not the public facade.

   Alternative considered: split `TdxTaskManager` into multiple public managers immediately. Rejected because it would create compatibility churn across CLI, catalog, presets, and tests.

2. Use a read-only boundary object with explicit dependencies.

   Rationale: read-only workflows still need access to `api_manager`, profile metadata, and artifact paths. Passing dependencies through a boundary object keeps test setup explicit and avoids hidden imports.

   Alternative considered: move helper functions as module-level globals only. Rejected because it would improve file size but not make ownership or dependencies clearer.

3. Start with a tracer slice.

   Rationale: `tdxquant/api/task.py` is large, and moving every report method in one change would make verification harder. A narrow slice proves the boundary shape before later migrations.

## Risks / Trade-offs

- Some read-only methods may still remain in `TdxTaskManager` after this slice → record that this is a boundary start, not a full task-manager split.
- Boundary delegation may look thin at first → include tests that prove ownership of at least one real read-only workflow through the new boundary.
- Import cycles with task helpers → keep the new module below `tdxquant/api/task.py` and inject dependencies rather than importing the facade.

## Migration Plan

1. Add red tests for the read-only boundary module and facade delegation.
2. Introduce the new read-only task boundary module.
3. Route the first selected read-only workflow through the boundary.
4. Run focused task tests and registry validation.
5. Update `FUNCTION_TREE.md`, archive OpenSpec, and repeat verification.
