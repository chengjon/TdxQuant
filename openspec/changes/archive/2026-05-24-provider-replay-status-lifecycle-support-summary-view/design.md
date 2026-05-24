# Design: Provider Replay Status Lifecycle Support Summary View

## Approach

Derive lifecycle support from the existing detailed `lifecycle` payload:

- `control_supported` is true only when start/stop, daemon, scheduler, or managed restart support is present.
- `managed_operation_count` is the count of supported lifecycle control categories.

For the current replay provider, the expected summary is `control_supported=false` and `managed_operation_count=0`.

## Boundary

The fields are summary evidence only. They do not introduce lifecycle operations and do not replace the detailed lifecycle payload or existing `boundaries` list.

## Validation

- Focused provider replay CLI summary test.
- Existing provider replay CLI and transport tests.
- OpenSpec strict validation.
- `FUNCTION_TREE.md` registry validation.
- Whitespace check before and after archive.

