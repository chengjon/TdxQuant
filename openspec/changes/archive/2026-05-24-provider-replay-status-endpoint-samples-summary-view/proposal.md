# provider-replay-status-endpoint-samples-summary-view

## Why

`FUNCTION_TREE.md` E-06 records provider replay fake-provider status as partially implemented. The status summary exposes a compact `endpoint_count`, but readers cannot see representative read-only endpoints without switching to the detailed payload.

Adding bounded endpoint samples improves summary usefulness while preserving the current boundary: the summary remains read-only, does not expose the complete endpoint list, and does not imply daemon lifecycle control or live provider availability.

## What Changes

- Add bounded `summary_view.capabilities.endpoint_samples` to `provider-replay status --view summary`.
- Add `endpoint_sample_limit` and `endpoint_sample_truncated` metadata.
- Keep full `capabilities.endpoints` out of the summary view.
- Add focused CLI tests and update `FUNCTION_TREE.md` E-06 evidence/boundary text.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Runtime behavior: no serving, probing, lifecycle, or endpoint implementation changes.
- Safety: summary remains a reduced projection over the existing detailed status payload.
- Registry: `FUNCTION_TREE.md` remains the single status/evidence/boundary registry.

