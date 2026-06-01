## Why

D-08 PingAn order paths now share execution preparation, but buy/sell/submit-once callsites still repeat desktop dispatch option conversion from `effective_profile`: delays, dialog timeouts, result-close behavior, final UIA capture, and fast order input-mode fields.

Those conversions are not product behavior; they are order dispatch adapter inputs. Keeping them inline in four callsites makes future profile changes easy to drift across buy, sell, and submit-once paths.

## What Changes

- Add an internal PingAn order dispatch options object that normalizes profile/callsite dispatch inputs.
- Route buy/sell/submit-once desktop dispatch calls through the options object when building runner kwargs.
- Keep method-specific desktop runner choice in the manager callsite.
- Preserve existing public manager, CLI, task, catalog, idempotency, risk-gate, lifecycle, broker-readiness, dispatch, finalize, and audit behavior.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## Impact

- Behavior: no intended external behavior change.
- Risk: low; the change is internal kwargs construction with focused manager tests and existing PingAn route regression coverage.
- Boundary: internal locality only; no new public API, CLI, task, catalog, workflow builder, desktop primitive, live readiness, or production trading readiness claim.
