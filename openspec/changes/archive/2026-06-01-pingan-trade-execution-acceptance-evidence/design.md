## Context

The repository already contains task-side artifacts for PingAn live/manual acceptance evidence, acceptance outcome coverage, readiness rollups, review packets, review result recording, and implemented-status transition writing. Those artifacts are intentionally fail-closed and separate from the trade execution path.

This change adds a trade-facing read-only summary that points at the implemented trade execution surface and its guard/evidence categories. It is not a new acceptance workflow engine and does not replace task-side promotion/readiness artifacts.

## Goals / Non-Goals

Goals:

- Provide a stable `TdxTradeManager.pingan.acceptance_evidence(...)` method.
- Provide a stable `trade acceptance-evidence` CLI command.
- Make side-effect boundaries machine-checkable: `dispatch_executed=false`, `order_submitted=false`, `workflow_dispatch_executed=false`, `desktop_automation_executed=false`, and `status_transition_executed=false`.
- Keep D-07/D-08 evidence easy to inspect without executing buy/sell/submit-once/confirm-current.

Non-goals:

- Do not execute PingAn trade commands.
- Do not call broker health, preflight, HID, UIA, process lifecycle, or task workflows.
- Do not evaluate live/manual acceptance artifacts for pass/fail; task-side review remains the promotion path.
- Do not edit FUNCTION_TREE status.

## Shape

The summary payload will include:

- schema/version and `execution_mode=readonly_trade_acceptance_evidence`.
- target nodes: D-07 and D-08.
- covered commands/methods for buy, sell, confirm-current, and submit-once.
- evidence categories for preflight, safety gates, lifecycle ownership, broker readiness guard, audit artifacts, task/manual acceptance artifacts, and review packets.
- artifact target paths for the local state/audit outputs.
- explicit false side-effect flags.
- a boundary string that prevents treating the summary as production readiness or workflow execution.

## Verification

- Red tests first for manager summary and CLI dispatch.
- Focused pytest for `tests/test_trade_manager.py` and `tests/test_api_cli.py`.
- `openspec validate --all --strict`.
- `git diff --check`.
- `python scripts/validate_function_tree_registry.py`.
