# Design: Subscription Summary Governance Reason Samples View

## Approach

The detailed `status_summary.governance.reasons` list remains the source of truth. The HTTP and CLI summary view builders will derive:

- `reason_count`: existing count field;
- `reason_samples`: the first `N` string reasons;
- `reason_sample_limit`: the configured bound;
- `reason_sample_truncated`: whether the detailed reason list has more entries than the samples.

The summary view still excludes the full `reasons` and `actions` arrays.

## Boundary

Reason samples are representative summary evidence only. They do not replace the detailed payload, do not guarantee exhaustive diagnosis, and do not trigger reconnect/backoff/restart/lifecycle behavior.

## Validation

- Focused CLI summary-view test.
- Focused HTTP summary-view test.
- OpenSpec strict validation.
- `FUNCTION_TREE.md` registry validation.
- Whitespace check before and after archive.

