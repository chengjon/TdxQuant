## Overview

Add an additive, read-only `governance.reason_source_counts` object to subscription long-run status summaries. The object is derived from existing detailed `governance.reasons` strings and is intended for compact status surfaces that should not expose the full reasons list.

## Data Shape

`governance.reason_source_counts` is a JSON object whose keys are reason sources and whose values are integer counts.

- `overall_status:reconnecting` contributes `overall_status: 1`.
- `heartbeat:stale` contributes `heartbeat: 1`.
- `watermark:stale` contributes `watermark: 1`.
- `reconnect:stale` contributes `reconnect: 1`.
- Malformed or non-string reasons contribute to `unknown`.
- Empty reasons produce `{}`.

Keys are emitted in sorted order for deterministic tests and fixture diffs.

## Summary View Projection

The HTTP and CLI summary views copy `governance.reason_source_counts` from the full governance object into their compact `governance` projection. They continue to omit the full `governance.reasons` list, exposing only `reason_count`, bounded `reason_samples`, and the new source counts.

## Boundary

The field is an advisory rollup only. It does not change reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior. It is not a complete reasons list, not an automated recovery policy, and not an execution instruction.
