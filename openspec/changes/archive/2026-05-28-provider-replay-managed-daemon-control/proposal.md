# Provider Replay Managed Daemon Control

## Why

E-06 now has a locked atomic lifecycle statefile ownership layer, but it still cannot start, inspect, or stop a tool-owned replay daemon. The next safe step is a minimal managed daemon control surface that uses the statefile owner token and config hash before any long-running supervisor or restart/backoff policy is introduced.

## What Changes

- Add managed daemon lifecycle helpers for start, status, and stop.
- Start launches `provider-replay serve --config <path>` as a background process, writes the owned lifecycle statefile, and returns the owner token.
- Status reads the lifecycle statefile, evaluates whether the recorded PID is currently running, and reports compact managed-daemon state.
- Stop requires an owner token, validates provider/config ownership, sends a termination signal only to the recorded owned PID, and writes a stopping state.
- Add `provider-replay daemon start|status|stop` CLI entries.
- Add focused tests using fake process launch/probe/terminate hooks.
- Update `FUNCTION_TREE.md` while keeping E-06 `[部分实现]`.

## Non-Goals

- No long-running supervisor loop.
- No restart/backoff scheduling.
- No automatic recovery.
- No port ownership inference.
- No process table command-line validation beyond the injected PID liveness probe.
- No real provider or broker lifecycle management.
- No claim that broker/workflow/write readiness is available.

