# Change: PingAn promotion readiness rollup artifact output

## Why

The PingAn promotion readiness rollup can now summarize gate status and reject stale evidence, but callers still need a stable artifact path to preserve exactly what was reviewed. Without an explicit output artifact, later reviews can accidentally cite regenerated terminal output or changed source evidence.

## What Changes

- Add an optional JSON output path to the read-only PingAn promotion readiness rollup task.
- Persist the rollup payload and minimal task metadata to the requested file.
- Return the artifact path in the task result for audit-friendly references.
- Register the artifact output boundary in `FUNCTION_TREE.md` without promoting D-07/D-08 status.

## Non-Goals

- No PingAn trade execution.
- No broker, desktop, lifecycle, catalog, report, or workflow execution.
- No automatic readiness promotion.
- No new default artifact write location; writes happen only when the caller provides a path.

