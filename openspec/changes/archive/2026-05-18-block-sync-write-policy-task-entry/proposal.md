# block-sync-write-policy-task-entry

## Why

`FUNCTION_TREE.md` E-04 records that block sync write policy hardening exists at the core contract level, but the high-level task/catalog path still does not expose that policy explicitly. Operators can call lower-level sync code with `write_policy`, yet the daily task surface still relies on `mode` plus `dry_run`, and the catalog has no safe dry-run entry for discovering the workflow.

This change adds a thin high-level entry for existing block sync write policies. It keeps provider schema and block mutation safety unchanged.

## What Changes

- Expose `write_policy` through block sync API manager, task manager, and CLI/task arguments.
- Add a stable dry-run block sync task preset and command catalog entry.
- Cover parser, task dispatch, preset default, and catalog plan behavior in focused tests.
- Update `FUNCTION_TREE.md` E-04 evidence and boundary.

## Capabilities

### Modified Capabilities

- `tdx-block-sync-write-policy`
- `tdx-task-management`
- `tdx-command-catalog`

## Impact

- Adds no provider capability and no new write path.
- Safe catalog entry defaults to `merge_dry_run`; real writes still require explicit non-dry-run policy or flags plus provider prerequisites.
- Existing `mode` / `dry_run` behavior remains compatible.

