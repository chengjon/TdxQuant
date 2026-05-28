## Why

`provider-replay status` can now report the configured managed replay daemon lifecycle surface, but `provider-replay lifecycle-readiness` still treats lifecycle controller, supervisor loop, and operator opt-in control as permanently missing. That makes readiness under-report E-06 progress after the managed lifecycle status work.

## What Changes

- Let lifecycle readiness count managed lifecycle controller, supervisor loop, and operator opt-in control when the detailed lifecycle status proves those surfaces are available.
- Let lifecycle readiness become ready only when all read-only prerequisites are satisfied: managed lifecycle status, valid statefile, and owned process diagnostics.
- Keep readiness non-executing: no start/stop/supervise/restart dispatch, no statefile writes, no process inspection unless explicitly requested through existing ownership diagnostics.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: lifecycle readiness should consume managed lifecycle status metadata instead of hard-coding lifecycle control prerequisites as missing.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected tests: `tests/test_api_cli.py`.
- Registry: `FUNCTION_TREE.md` E-06 evidence/boundary note.
