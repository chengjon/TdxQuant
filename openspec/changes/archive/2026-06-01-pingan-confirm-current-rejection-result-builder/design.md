## Context

The confirm-current seam already owns gate-before-dispatch and finalize decisions. The manager still provides a nested `build_boundary_rejection_result(...)` callback because the exact rejection payload depends on caller-resolved confirm-current inputs:

- `close_result_dialog`
- resolved lookup and timeout values
- lifecycle owner-lock inputs
- broker-readiness requirement flag

This change introduces a small immutable context object for those values and a pure builder function in the seam module.

## Goals

- Move the boundary rejection result shape into `tdxquant/trade/pingan_execution.py`.
- Preserve owner-lock and broker-readiness rejection messages, result codes, next actions, checks, and input echo.
- Keep the manager responsible only for resolving inputs, building the context, applying gates, and wiring the seam.

## Non-Goals

- Do not move dialog lookup/click dispatch code.
- Do not modify public manager parameters.
- Do not introduce generic workflow infrastructure.

## Compatibility

The public `confirm_current` result shape stays unchanged for gate rejection, failed lookup/click, warning, and success paths.

## Validation

- Add direct builder tests for owner-lock rejection and broker-readiness rejection.
- Run the focused PingAn trade execution/manager/gateway suite.
- Run OpenSpec validation, diff check, and FUNCTION_TREE registry validation.

