## 1. Task workflow formalization

- [x] 1.1 Add a stable `task block-read-full` requirement to the task-management spec covering both `TdxTaskManager.block_read_full(...)` and `task block-read-full`.
- [x] 1.2 Document that task-level block read full remains a single-read diagnostics wrapper around `manager.block.read_watchlist_snapshot(...)`, preserves canonical `data.snapshot`, and only adds task-level `data.read_full`.

## 2. Lifecycle sync

- [x] 2.1 Verify the existing implementation and focused tests already cover task-manager dispatch, CLI parsing, and CLI dispatch for `task block-read-full`.
- [x] 2.2 Sync the approved task-block-read-full contract into the main OpenSpec spec set.

## 3. Validation and archive

- [x] 3.1 Run `openspec validate task-block-read-full-entrypoint --type change --strict`.
- [x] 3.2 Archive the completed change after spec sync.
