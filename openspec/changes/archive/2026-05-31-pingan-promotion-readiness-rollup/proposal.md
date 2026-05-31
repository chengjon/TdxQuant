## Why

D-07/D-08 now have separate provider/safety, lifecycle, audit, automated outcome, and manual acceptance evidence surfaces. Operators still need a single read-only rollup that shows which promotion gates are complete, which remain incomplete, and why the nodes must remain `[部分实现]`.

## What Changes

- Add a read-only PingAn promotion readiness rollup task that consumes existing evidence JSON files.
- Summarize provider/broker ownership, safety gates, desktop lifecycle, automated audit outcome coverage, live/manual acceptance, and full acceptance gates.
- Add a stable CLI entry under `task pingan-promotion-readiness-rollup`.
- Register the rollup in `FUNCTION_TREE.md` D-07/D-08 without status promotion.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-management`: add a stable read-only PingAn promotion readiness rollup task workflow.
- `tdx-desktop-trading-safety`: add a safety requirement that the rollup remains evidence-only and non-executing.
- `tdx-function-tree-registry`: register D-07/D-08 rollup evidence while preserving `[部分实现]`.

## Impact

- Code: `tdxquant/api/task.py`, `tdxquant/cli.py`
- Tests: `tests/test_api_manager.py`, `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`
- Registry/specs: `FUNCTION_TREE.md`, `openspec/specs/**`
- No external dependency, no broker execution, no desktop control, and no automatic status promotion.
