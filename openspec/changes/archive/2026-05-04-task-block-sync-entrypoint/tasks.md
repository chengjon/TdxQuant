## 1. Task workflow formalization

- [x] 1.1 Add a stable `task block-sync` requirement to the task-management spec covering both `TdxTaskManager.block_sync(...)` and `task block-sync`.
- [x] 1.2 Document that task-level block sync remains a thin wrapper around `manager.block.sync_watchlist(...)` and preserves the provider-level `data.sync` / `data.block_mutation` contract.

## 2. Lifecycle sync

- [x] 2.1 Verify the existing implementation and focused tests already cover task-manager dispatch, CLI parsing, and CLI dispatch for `task block-sync`.
- [x] 2.2 Sync the approved task-block-sync contract into the main OpenSpec spec set.

## 3. Validation and archive

- [x] 3.1 Run `openspec validate task-block-sync-entrypoint --type change --strict`.
- [x] 3.2 Archive the completed change after spec sync.
