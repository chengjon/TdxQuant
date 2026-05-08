# Task Block Sync Design - Review

Reviewer: Claude
Date: 2026-05-03
Document: `docs/superpowers/specs/2026-05-03-task-block-sync-design.md`

## Overall Verdict

Design is sound and well-scoped. The "thin wrapper" choice is correct given the current architecture maturity. Below are concrete findings grouped by category.

---

## Strengths

1. **Scope discipline is excellent.** The spec explicitly excludes preset/catalog/file-import and justifies each exclusion. This is the right call — the provider-level `sync_watchlist` stabilized only recently, and the task layer should prove its value before accumulating productization features.

2. **Non-redefinition principle is clearly stated and correct.** Section 4 (Error Semantics) and Section 3 (Response Shape) explicitly forbid task-specific state translation. This prevents the common anti-pattern where a wrapper layer introduces divergent error semantics.

3. **Approach comparison is honest.** Options B and C are fairly presented with their actual merits, not straw-manned.

4. **Testing strategy is pragmatic.** The distinction between "test the wrapper" and "don't retest the underlying orchestration" shows awareness of test layering.

---

## Findings

### F1. `stock[]` parameter naming inconsistency [Medium]

**Section 2** uses `stock[]` as the field name, but the existing provider-level API uses `symbols` everywhere:

- `BlockApi.sync_watchlist(block_code, symbols, ...)` in `tdxquant/api/block.py:107-108`
- `sync_watchlist_to_block(..., symbols: list[str], ...)` in `tdxquant/block_sync.py:173`
- CLI flat command uses `--stock` which maps to `symbols` param in `cli.py:2785`

The spec should decide: does `TdxTaskManager.block_sync()` take `symbols` (consistent with provider) or `stock` / `stocks` (consistent with CLI `--stock` flag)?

**Recommendation:** Use `symbols` in the Python API to match the provider layer. The CLI can keep `--stock` for ergonomics, just as the flat CLI already does. Document the mapping explicitly.

### F2. Missing `_attach_task_metadata` in Response Shape [Medium]

**Section 3** says the response "directly reuses provider-level result structure" and only mentions adding `task_name` and `invoked_via`. But every existing task method uses `_attach_task_metadata()` which adds:

- `result.data["task"] = {"entrypoint": "TdxTaskManager", "name": task_name}`
- `result.data["task_profile"] = {"name": ..., "options": ...}`
- `result.data["timing"] = {...}`

The spec should either:
- Acknowledge that `_attach_task_metadata` will be used (making the response slightly richer than pure passthrough), or
- Explicitly decide to skip it and explain why `block_sync` is different from other task methods.

**Recommendation:** Use `_attach_task_metadata` for consistency with all other task methods. The spec should acknowledge this in Section 3.

### F3. No mention of `audit_dir` passthrough [Low]

The provider-level `sync_watchlist` accepts an optional `audit_dir` parameter (`block.py:116`). The spec's Request Shape (Section 2) does not list `audit_dir`.

If the task layer omits `audit_dir`, the underlying provider will write audit logs to the default `runtime/block-sync/` directory. This is probably fine for v1, but it should be an explicit decision.

**Recommendation:** Either include `audit_dir` as a passthrough parameter, or add a Non-Goal stating that task-level audit log location customization is deferred.

### F4. `show` parameter semantics are unclear in task context [Low]

**Section 2** lists `show` as "passthrough to underlying layer." The `show` flag in `sync_members` controls whether the TongDaXin UI shows the block after modification. This is a UI-level concern.

For a task/programmatic entry point, the default should arguably be `False` (no UI show), since tasks are typically non-interactive. The spec doesn't discuss the default value.

**Recommendation:** The spec should state the default for `show` in the task context and justify it. Consider defaulting to `False` for `TdxTaskManager.block_sync()`, since the CLI already defaults to `True` for interactive use.

### F5. No mention of `strategy_path` [Low]

`BlockApi` and `BlockApi.sync_watchlist` accept `strategy_path` (the TongDaXin strategy file path). The task manager already holds `self.strategy_path` and passes it through to the API manager. The spec should confirm that the task layer will use the profile-configured `strategy_path` rather than requiring it as an explicit parameter.

**Recommendation:** Add one sentence in Section 1 or Section 2 confirming that `strategy_path` comes from the task profile, not from the task method signature.

### F6. CLI subcommand registration not specified [Low]

The spec shows the CLI invocation:

```bash
python -m tdxquant.cli task block-sync --block-code ZXG ...
```

But doesn't specify:
- Which argument group this falls under (the existing pattern has `task_subparsers.add_parser("block-sync")`)
- The exact argparse configuration for `--stock` (repeatable `action="append"` vs. `nargs="+"`)
- Whether it follows the existing `_add_task_common_arguments` pattern

**Recommendation:** Add a brief subsection under Section 5 specifying the CLI registration pattern, or at minimum state that it follows the same argparse pattern as other task subcommands.

### F7. Missing `_capture_task_timing` in spec [Low]

All existing task methods use the pattern:

```python
result, timing = _capture_task_timing("task.block_sync", run)
return self._attach_task_metadata(result, task_name="block_sync", timing=timing)
```

The spec should explicitly show this as the implementation pattern to avoid a naive implementation that just calls `self.api_manager.block.sync_watchlist(...)` without the timing/metadata wrapper.

**Recommendation:** Add an implementation sketch in Section 1 or Section 3 showing the `run()` closure + `_capture_task_timing` + `_attach_task_metadata` pattern.

---

## Observations (not actionable, for awareness)

1. **The design is consistent with the project's stated direction.** `TdxQuant_Next_Steps.md` Section 4, Direction E explicitly identifies "higher-level task entry point for block sync" as remaining work. This spec directly addresses that.

2. **Risk #1 (redefining bottom contract) is well-mitigated** by the explicit "task layer does not translate states" rule. This is the most important architectural guardrail in the spec.

3. **The Open Questions section says "none"**, which is appropriate given the narrow scope. If the review above raises questions that need resolution, they should be promoted there.

---

## Summary

| ID | Severity | Topic |
|----|----------|-------|
| F1 | Medium | `stock[]` vs `symbols` naming — should match provider API |
| F2 | Medium | Missing `_attach_task_metadata` acknowledgment in Response Shape |
| F3 | Low | `audit_dir` passthrough decision not stated |
| F4 | Low | `show` default value for task context not discussed |
| F5 | Low | `strategy_path` source not confirmed |
| F6 | Low | CLI argparse registration pattern not specified |
| F7 | Low | `_capture_task_timing` pattern not shown in implementation sketch |

**Bottom line:** The spec is ready to implement with F1 and F2 addressed. The Low items are clarifications that prevent ambiguity during implementation but don't affect architectural soundness.
