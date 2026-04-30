## Context

The stable trade line already distinguishes:

- environment readiness via `trade health`
- single-request readiness via `trade preflight`

What remains less formalized is whether the stable dialog lookup path itself can identify the current confirm or result dialog when those dialogs are visible. Right now that logic is embedded inside the side-effecting buy flows, especially around:

- confirm lookup
- result dialog lookup
- result confirm-button lookup
- UIA vs experimental Win32 lookup fallback behavior

This package lifts those lookups into a read-only management workflow without changing the execution path.

## Goals / Non-Goals

**Goals:**
- Expose `TdxTradeManager.pingan.dialog_readiness(...)` as a stable read-only workflow.
- Expose `trade dialog-readiness` in the nested trade CLI.
- Reuse the same dialog lookup mode semantics as the stable trade execution path.
- Let callers choose between passive observation and `require_visible` enforcement.

**Non-Goals:**
- Do not click, focus, or close any dialog.
- Do not execute submit or confirm actions.
- Do not redesign existing buy workflow dialog handling.
- Do not add trade preset support in this slice.

## Decisions

### 1. Dialog readiness targets currently visible dialogs only

This workflow will not fabricate a “future dialog guarantee.” It answers whether the current visible confirm/result dialog can be located right now using the stable lookup rules. If no such dialog is visible:

- return `warning` when `require_visible` is false
- return `failed` when `require_visible` is true

### 2. Reuse stable dialog lookup mode semantics

The workflow will honor the same lookup mode choices already used by stable trade execution:

- `uia`
- `win32_experimental`

For `win32_experimental`, the workflow will preserve fallback semantics and report the chosen/fallback mode in the check detail.

### 3. Keep confirm and result checks individually addressable

The workflow will support:

- `dialog=confirm`
- `dialog=result`
- `dialog=both`

and will emit separate named checks so operators can see exactly which stage is ready.

## Risks / Trade-offs

- [Callers may overread readiness as a future execution guarantee] → Keep wording explicit that this only checks currently visible dialogs.
- [No visible dialog may be a normal state] → Support passive observation mode with warnings instead of hard failure.
- [Private lookup helpers may drift] → Reuse the stable execution path’s existing lookup behavior rather than re-implementing different rules.

## Migration Plan

1. Add RED tests for manager and CLI behavior.
2. Implement read-only dialog readiness workflow.
3. Add nested CLI parser and dispatch.
4. Update docs, validate, and archive.
