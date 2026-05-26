# Design: Subscription Summary Runtime PID Source

## Behavior

The existing HTTP and CLI summary runtime helpers already copy `control.pid` to `runtime.pid` when the control status includes a `pid` key. This change adds `runtime.pid_source = "control"` in the same branch.

The field is intentionally omitted when `runtime.pid` is omitted. It is not a health signal, ownership proof, readiness proof, or lifecycle-control field.

## Compatibility

The change is additive and opt-in to summary view responses. Existing detailed payloads remain unchanged. Existing consumers that ignore unknown fields remain compatible.

## Verification

- Add/update HTTP summary view tests asserting `runtime.pid_source`.
- Add/update CLI summary view tests asserting `runtime.pid_source`.
- Run focused bridge HTTP and API CLI suites.
- Run OpenSpec strict validation, diff check, and the FUNCTION_TREE registry validator.
