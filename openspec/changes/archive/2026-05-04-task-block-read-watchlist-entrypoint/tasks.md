## 1. Task workflow formalization

- [x] 1.1 Add a stable `task block-read-watchlist` requirement to the task-management spec covering both `TdxTaskManager.block_read_watchlist(...)` and `task block-read-watchlist`.
- [x] 1.2 Document that task-level block read watchlist remains a thin wrapper around `manager.block.read_watchlist_snapshot(...)` and preserves the provider-level `data.snapshot` contract.

## 2. Lifecycle sync

- [x] 2.1 Verify the existing implementation and focused tests already cover task-manager dispatch, CLI parsing, and CLI dispatch for `task block-read-watchlist`.
- [x] 2.2 Sync the approved task-block-read-watchlist contract into the main OpenSpec spec set.

## 3. Validation and archive

- [x] 3.1 Run `openspec validate task-block-read-watchlist-entrypoint --type change --strict`.
- [x] 3.2 Archive the completed change after spec sync.
