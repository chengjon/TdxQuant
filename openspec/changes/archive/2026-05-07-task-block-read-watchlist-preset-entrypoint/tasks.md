## 1. Preset entrypoint formalization

- [x] 1.1 Add a stable task-preset requirement for `block-read-watchlist` to the task-management spec.
- [x] 1.2 Document that preset defaults use static `block_code` only, without modifying the preset schema.

## 2. Lifecycle sync

- [x] 2.1 Verify the existing implementation and focused tests already cover preset listing, `task run --preset ...` dispatch, explicit `--block-code` override semantics, and missing-required-field failure behavior.
- [x] 2.2 Sync the approved preset-entry contract into the main OpenSpec spec set.

## 3. Validation and archive

- [x] 3.1 Run `openspec validate task-block-read-watchlist-preset-entrypoint --type change --strict`.
- [x] 3.2 Archive the completed change after spec sync.
