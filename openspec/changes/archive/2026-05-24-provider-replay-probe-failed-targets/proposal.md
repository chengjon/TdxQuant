## Why

`FUNCTION_TREE.md` keeps E-06 fake provider as partial because replay status is still being hardened as a read-only daemon boundary registry. The current `runtime.probe_summary` reports `failed_count` and `unhealthy` targets, but it does not expose a `failed` target list matching the `failed_count` name.

Adding `runtime.probe_summary.failed` makes failed probe targets explicit without changing probe execution, socket startup, daemon lifecycle, or write behavior.

## What Changes

- Add additive `runtime.probe_summary.failed` to provider replay status.
- Keep `failed` aligned with `failed_count` and the current unhealthy target classification.
- Cover detailed status and summary-view projection through tests.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary.

## Non-Goals

- No new probe endpoints or probe scheduling.
- No socket startup, daemon lifecycle management, restart/backoff, or write support.
- No exposure of full probe payloads, bearer tokens, allowlist members, or fixture paths.
