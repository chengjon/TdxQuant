## Context

The project already documents a target architecture with query API management, task/report/catalog facades, provider replay, and a separate desktop trading line. The implementation still concentrates several unrelated reasons to change inside large modules:

- `tdxquant/cli.py` owns root parser composition, nested command parsers, flat command compatibility, catalog planning, bridge control, provider replay commands, and legacy Win32/HID routines.
- `tdxquant/api/manager.py` repeats the same manager-call pattern across many domain proxy methods.
- `tdxquant/api/task.py` combines task orchestration, report aggregation, ledger parsing, export writing, subscription watch, block workflows, and trade wrappers.
- `tdxquant/api/bridge.py` remains the live runtime bridge and also contains provider health, subscription, mutation, serialization, and platform probing logic.

The change must preserve existing CLI compatibility and provider result contracts because the project uses many runtime JSON presets, replay fixtures, and large regression test files as behavior anchors.

## Goals / Non-Goals

**Goals:**

- Improve locality for future changes by moving stable command families toward dedicated command modules.
- Reduce repeated manager proxy mechanics by introducing a shared manager-call envelope.
- Make runtime configuration loading and validation a first-class registry surface instead of scattered JSON reads.
- Make capability risk classification explicit for query/read-only, provider mutation, native trade mutation, and desktop trade mutation surfaces.
- Preserve public CLI names, manager method names, replay-mode behavior, provider result payload shape, and flat command compatibility.

**Non-Goals:**

- No removal of legacy flat commands.
- No change to the TongDaXin live bridge implementation contract.
- No replacement of `TdxTaskManager`, `TdxApiManager`, `TdxTradeManager`, or existing runtime JSON file formats.
- No broad rewrite of desktop UIA/Win32/HID automation.
- No introduction of third-party dependencies solely for this refactor.

## Decisions

### Decision 1: Extract command families incrementally

The first command extraction will target nested `api` commands because they already have a coherent parser and dispatcher block, broad test coverage, and lower desktop-environment risk than legacy Win32/HID flat commands.

Alternative considered: split the entire `tdxquant/cli.py` at once. This would improve size faster but has too much regression risk because the file contains multiple compatibility layers and many historical command paths.

### Decision 2: Use a shared manager-call envelope without changing public manager methods

`TdxApiManager` will gain a small helper method that executes a manager call with optional replay dispatch, timing capture, effective profile construction, and metadata attachment. Domain proxy methods will migrate to the helper over time while preserving their current public signatures and result payloads.

Alternative considered: replace proxy classes with generated dispatch tables. That would reduce code volume, but it would make typed method signatures less clear and increase risk for existing tests and callers.

### Decision 3: Add a central runtime config registry first, then migrate callers

The registry will initially centralize path discovery and JSON-object validation for existing runtime config files. Callers can migrate gradually from direct loaders to registry-backed loaders while keeping current file formats.

Alternative considered: introduce a full JSON schema validator. That would be stronger, but the project currently avoids extra dependencies and has many evolving config shapes.

### Decision 4: Represent capability risk metadata as stable data, not comments

The architecture boundary will expose risk classes through a small metadata module so tests and future catalog/provider surfaces can consume the same classification. This avoids burying the query/trade distinction only in docs.

Alternative considered: only document the distinction in `FUNCTION_TREE.md` and design docs. That would not prevent drift in code paths that add new commands or catalog entries.

## Risks / Trade-offs

- Parser extraction could change argparse behavior or help text ordering. Mitigation: reuse the same argument definitions and run the existing API CLI tests.
- Manager-call envelope could subtly change provider metadata fields. Mitigation: migrate a small read-only domain first and assert existing provider fields remain stable.
- Risk classification could be confused with authorization or safety enforcement. Mitigation: name it as metadata and keep enforcement behavior unchanged in this change.
- Runtime config registry could drift from existing loaders. Mitigation: make existing loaders delegate only after focused tests prove paths and validation remain equivalent.

## Migration Plan

1. Add OpenSpec requirements and task plan.
2. Add `tdxquant/architecture.py` for capability risk metadata.
3. Add `tdxquant/runtime_config.py` for runtime config paths and JSON-object validation.
4. Add `tdxquant/cli_api.py` and make the root CLI delegate nested `api` parser/handler ownership to it.
5. Add the manager-call envelope and migrate a narrow subset of manager proxy methods.
6. Run focused tests and full relevant regressions.
7. Leave larger `task.py`, provider adapter extraction, and legacy flat-command cleanup as subsequent OpenSpec tasks if they cannot be completed safely in the first implementation slice.

## Open Questions

- Should `TdxApiManager.trade` remain public long term, or should native trade mutation calls move behind a separate risk-gated facade?
- Should runtime config validation eventually become strict schema validation with explicit per-file shape contracts?
- Which legacy flat command family should be extracted after nested `api`: catalog, bridge, or provider replay?
