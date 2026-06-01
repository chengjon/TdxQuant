## Context

The order seam has a stable branch contract and direct coverage for success, duplicate, conflict, and failed gate paths. The next locality improvement is at the call boundary: the seam depends on a set of callbacks that belong together.

`PingAnOrderExecutionHandlers` will group those callbacks. Existing direct tests and manager behavior should continue to pass. The older callback parameters will remain accepted so existing internal callers are not broken abruptly.

## Goals

- Introduce one internal handler bundle for order seam callbacks.
- Keep `execute_pingan_order` behavior unchanged.
- Update manager order paths to pass `handlers=` instead of repeating callback lambdas at every callsite.
- Add direct test coverage proving `execute_pingan_order` accepts and uses the handler bundle.

## Non-Goals

- Do not change public manager method signatures.
- Do not remove legacy callback parameters in this slice.
- Do not alter order dispatch or artifact behavior.

## Compatibility

Public behavior remains unchanged. Existing tests using legacy callback parameters continue to pass, and new code can use `handlers=` as the preferred internal call shape.

## Validation

- Add a focused direct seam test for `PingAnOrderExecutionHandlers`.
- Run focused PingAn trade execution/manager/gateway tests.
- Run OpenSpec validation, diff check, and FUNCTION_TREE registry validation.

