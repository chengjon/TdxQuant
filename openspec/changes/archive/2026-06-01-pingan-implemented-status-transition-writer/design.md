## Context

The existing chain can produce a transition gate with `eligible_for_status_transition_review=true`. A real status transition still needs a separate, auditable writer because changing `FUNCTION_TREE.md` is the project's feature registry source of truth. The writer must be explicit, reversible by git, and impossible to trigger through catalog/workflow execution.

## Goals / Non-Goals

**Goals:**

- Add `TdxTaskManager.pingan_implemented_status_transition(...)`.
- Require `transition_gate_path`, `function_tree_path`, `output_path`, `operator`, `reason`, and `confirm_transition=true`.
- Require `apply=true` and `dry_run=false` before modifying the function tree or writing the transition record.
- Validate that D-07 and D-08 currently have status `[部分实现]` before changing them to `[已实现]`.
- Write a transition record artifact with schema `tdx.desktop_trade.pingan_implemented_status_transition_record.v1`.

**Non-Goals:**

- Do not execute PingAn broker, desktop, trade, report, catalog, bundle, or task workflows.
- Do not generate or refresh readiness evidence.
- Do not automatically discover FUNCTION_TREE paths or transition arbitrary nodes.
- Do not run the writer against the repository registry in this slice; repository D-07/D-08 stay `[部分实现]` until an explicit operator transition is executed with real artifacts.

## Decisions

- The writer supports dry-run and apply mode. Dry-run returns a transition plan and record preview without writing files.
- Apply mode requires both `apply=true` and `confirm_transition=true`. This prevents a caller from accidentally changing the registry because they supplied a valid gate.
- The function-tree path is caller-provided so tests can exercise real file mutation against a temporary copy without changing the repository registry.
- The transition record is written only on successful non-dry-run apply. It records before/after statuses, gate path, operator, reason, and explicit no-trading flags.
- The writer appends no new evidence text itself. Evidence registration in the repository remains a normal reviewed code change.

## Risks / Trade-offs

- This adds a code path capable of changing `FUNCTION_TREE.md`. To keep the blast radius small, it is limited to D-07/D-08, requires an eligible gate, requires current status `[部分实现]`, and requires explicit apply/confirmation flags.
- The repository rows remain partial after this slice. That is intentional because implementing the writer is not the same as executing a real transition using operator-provided live artifacts.
