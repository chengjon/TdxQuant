## Context

The project already distinguishes stable desktop trade workflows from lower-level probes, but operators still need a stable answer to whether the current Ping An trading path is ready before a side-effecting order attempt. Today that information is fragmented across:

- broker adapter `health_check()`
- low-level desktop probe commands
- HID ping commands
- implicit trade profile and artifact-path assumptions

This package deliberately does not merge all diagnostics into a single deep probe. It only lifts the most important non-side-effecting readiness checks into the stable trade management surface.

## Goals / Non-Goals

**Goals:**
- Expose `TdxTradeManager.pingan.health(...)` as a stable read-only health workflow.
- Expose `trade health` in the nested trade CLI.
- Include broker/runtime window readiness.
- Include current trade profile context and artifact target paths.
- Optionally include HID ping when a port is provided.
- Guarantee the workflow does not write order state, event log, or submission ledger rows.

**Non-Goals:**
- Do not execute any buy-page mutation or confirmation flow.
- Do not replace existing low-level probe commands.
- Do not add trade preset execution for health in this slice.
- Do not redesign provider-wide `health` / `doctor` semantics.

## Decisions

### 1. Health stays on the stable Ping An trade proxy

The new workflow will live at `TdxTradeManager.pingan.health(...)`, matching the existing stable `buy(...)` and `buy_submit_once(...)` management surface. This avoids introducing a second parallel trade facade just for diagnostics.

### 2. Health is read-only and does not use trade finalization side effects

Stable trade execution currently routes through `_finalize_result(...)`, which writes last-order state, append-only event logs, and optional submission-ledger entries. The health workflow must not call that path. It will attach manager/profile metadata directly and return a summary payload without persisting trade artifacts.

### 3. HID ping is opt-in through the provided port

If the caller does not provide `port`, the workflow reports that HID ping was skipped. If the caller provides `port`, the workflow will attempt a live `PING` against the HID bridge using the supplied `baudrate`, `timeout`, and `pre_delay`. This keeps the default health check non-invasive while still allowing operators to validate the exact hardware bridge path they intend to use.

### 4. Health returns structured checks plus an overall status

The workflow will normalize checks into a small structured summary:

- `broker_runtime`
- `hid_ping`

It will also return:

- `overall_status`
- `artifact_targets`
- `requested` parameters

Top-level `Result.ok` will be `False` only when required checks fail. Optional or skipped checks may still yield a degraded-style summary without forcing a hard failure.

## Risks / Trade-offs

- [Health may be mistaken for full buy-page readiness] → Keep the summary explicit that it covers broker/runtime and optional HID path, not deep page-specific diagnostics.
- [Operators may expect artifact files to exist afterward] → Return `artifact_targets` instead of created artifact paths, and test that no files are written.
- [HID ping may fail for reasons unrelated to runtime/window readiness] → Keep HID ping opt-in and expose it as a separate named check.

## Migration Plan

1. Add RED tests for manager, CLI parser, and CLI dispatch.
2. Implement read-only health workflow on the stable Ping An trade proxy.
3. Add nested `trade health` parsing and dispatch.
4. Update docs, validate, and archive.
