# Design

## Context

`tdxquant/block_watchlist_import.py` already validates JSON import files, produces dry-run plans, and delegates execution to `sync_watchlist_to_block`. The missing layer is an operator-facing task/catalog wrapper that can be discovered and planned like the existing block read/watchlist entries.

## Goals

- Expose `block-watchlist-import` as a task subcommand.
- Allow task presets and catalog entries to resolve the import wrapper without inventing a new schema.
- Preserve the existing `block.sync_watchlist` execution path and audit semantics.
- Keep the default catalog preset plan-oriented so discovery and planning are safe in non-live environments.

## Non-Goals

- Do not add CSV/TXT import support.
- Do not add bidirectional sync or source-file writeback.
- Do not bypass block sync mutation_key, dry-run, or audit handling.
- Do not make catalog metadata the source of truth for whether a real provider environment is available.

## Decisions

### 1. Add a task wrapper rather than a new API domain

The existing import adapter is already local-file orchestration around block sync. A task wrapper matches the existing block watchlist task surface and avoids adding a parallel manager concept.

### 2. Reuse task preset and catalog mechanics

The preset will resolve through the existing `task run --preset` and catalog `task` source path. This keeps catalog behavior consistent with block read and export entries.

### 3. Preserve explicit apply semantics

The task wrapper accepts `--dry-run/--no-dry-run` and forwards the resolved value to the import adapter. The catalog preset is intended for plan/discovery and does not execute during `catalog plan`.

## Risks / Trade-offs

- A live `--no-dry-run` run can mutate a provider block. The wrapper does not reduce the existing block sync safeguards, and tests focus on parser/dispatch/plan paths.
- The default catalog entry requires a concrete JSON path. A preset-owned runtime path is acceptable as a stable example, but callers can override it with `--input`.
