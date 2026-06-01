## Context

The confirm-current manager dispatch callback still performs real desktop-adjacent operations:

- find the current confirm dialog,
- click confirm,
- inspect the result dialog,
- optionally close the result dialog.

Those operations should remain in the manager path for this slice. However, the returned `Result` shapes for lookup failure, click failure, and advanced/warning completion are pure payload construction and can be tested directly.

## Goals

- Introduce `PingAnConfirmCurrentDispatchContext` for resolved confirm-current inputs.
- Introduce `build_pingan_confirm_current_dispatch_result(...)` for the shared confirm-current result envelope.
- Preserve existing result codes, messages, input echo, requested fields, checks, result-dialog payload, warnings, and next action.
- Keep the manager responsible for UI lookup/click and health-check construction.

## Non-Goals

- Do not move UI lookup/click code.
- Do not change manager public parameters.
- Do not introduce generic workflow infrastructure.

## Compatibility

The public `confirm_current` result shape stays unchanged for failed lookup, failed click, warning, and success paths.

## Validation

- Add direct builder tests for failed lookup and advanced/warning completion.
- Run the focused PingAn trade execution/manager/gateway suite.
- Run OpenSpec validation, diff check, and FUNCTION_TREE registry validation.

