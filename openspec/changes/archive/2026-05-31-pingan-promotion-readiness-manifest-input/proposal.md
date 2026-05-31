# Change: PingAn promotion readiness manifest input

## Why

The PingAn promotion readiness rollup can read evidence paths, reject stale files, and write a JSON artifact. Operators still need a stable manifest that records which evidence artifacts and freshness cutoff belong to a review. Passing many paths directly on the command line makes later audits harder to reproduce.

## What Changes

- Add an optional read-only evidence manifest JSON input to the PingAn promotion readiness rollup task.
- Let the manifest provide preflight, dialog readiness, acceptance coverage, freshness cutoff, and expected gate names.
- Keep direct CLI arguments as explicit overrides for manifest-provided values.
- Surface manifest metadata in the rollup output and register the boundary in `FUNCTION_TREE.md`.

## Non-Goals

- No evidence generation or refresh.
- No PingAn trade execution.
- No broker, desktop, lifecycle, report, catalog, or workflow execution.
- No automatic D-07/D-08 status promotion.

