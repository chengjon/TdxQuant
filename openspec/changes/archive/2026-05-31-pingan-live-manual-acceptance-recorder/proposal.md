# PingAn Live Manual Acceptance Recorder

## Why

D-07/D-08 promotion readiness currently can consume a `tdx.desktop_trade.pingan_live_manual_acceptance.v1` JSON file, but the file is still external to the task surface. That leaves the most important manual acceptance evidence as an unmanaged hand-written artifact.

## What Changes

- Add a `TdxTaskManager.pingan_live_manual_acceptance(...)` task that writes a controlled live/manual acceptance JSON artifact.
- Add a `task pingan-live-manual-acceptance` CLI entry.
- Add a dry-run discovery preset and catalog entry for the recorder.
- Keep the recorder explicitly non-trading: it records operator-provided acceptance evidence only and does not execute PingAn workflows.
- Update `FUNCTION_TREE.md` D-07/D-08 as `[部分实现]` evidence, not implemented status.

## Non-Goals

- Do not execute buy/sell/confirm/current workflows.
- Do not infer live acceptance from audit entries.
- Do not auto-generate acceptance without explicit operator-provided outcomes.
- Do not claim broker production readiness or D-07/D-08 implemented status.
- Do not auto-promote `FUNCTION_TREE.md` status.

