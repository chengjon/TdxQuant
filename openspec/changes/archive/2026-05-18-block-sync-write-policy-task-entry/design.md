# Design

## Context

Core block sync already resolves `write_policy` values such as `replace`, `merge`, `replace_dry_run`, and `merge_dry_run`, and returns conflict feedback when `mode` or `dry_run` disagree with an explicit policy. The remaining gap is exposure through the operator-facing task and catalog layers.

## Decision

Add `write_policy` as an optional parameter on the existing block sync path:

- CLI/API parser: `--write-policy {replace,merge,replace_dry_run,merge_dry_run}`
- `TdxBlockApi.sync_watchlist(...)`
- manager block proxy `sync_watchlist(...)`
- `TdxTaskManager.block_sync(...)`
- task dispatch for `task block-sync`

Add a preset named `plan-zxg-block-sync-merge` with:

- command `block-sync`
- profile `default`
- api profile `safe_read`
- options `block_code=ZXG`, `stock=[000001.SZ, 600519.SH]`, `write_policy=merge_dry_run`, `show=true`

Add a catalog task-source entry for discovery and planning. The entry is intentionally named as a plan/dry-run workflow so readers do not infer that catalog discovery performs provider writes.

## Non-Goals

- Do not add provider schema fields.
- Do not bypass `mutation_key` replay/conflict handling.
- Do not convert catalog `run` into an execution recommendation.
- Do not add CSV/TXT import or source file writeback.

