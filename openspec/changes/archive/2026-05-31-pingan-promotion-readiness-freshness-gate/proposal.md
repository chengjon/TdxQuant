# Change: PingAn promotion readiness evidence freshness gate

## Why

`pingan-promotion-readiness-rollup` can summarize existing PingAn promotion evidence, but it still needs a way to distinguish fresh evidence from stale operator-provided JSON artifacts. Without a freshness gate, stale files can look like current readiness and overstate D-07/D-08 progress.

## What Changes

- Extend the read-only promotion readiness rollup with optional evidence freshness thresholds.
- Treat stale or unreadable evidence as incomplete for the affected gate.
- Surface freshness status in the rollup output so FUNCTION_TREE evidence can cite freshness boundaries explicitly.
- Add a CLI option so operators can require evidence younger than a chosen cutoff.

## Non-Goals

- No PingAn trade execution.
- No broker control, desktop control, lifecycle restart, or process ownership changes.
- No automatic promotion of D-07/D-08.
- No change to existing task/report/trade execution semantics outside this read-only rollup.

