## Why

Direct task trade commands can now opt into the PingAn owner-lock execution guard, but `task run --preset ...` still cannot pass the same guard via CLI overrides. That keeps preset-driven execution from using the same explicit safety control as direct task execution.

## What Changes

- Add lifecycle owner-lock guard override arguments to `task run`.
- Preserve preset-provided guard options while allowing explicit CLI values to override them.
- Forward resolved guard options from preset execution to `trade-buy`, `trade-sell`, and `trade-submit-once` task workflows.
- Register this preset/run coverage in `FUNCTION_TREE.md` as partial D-07/D-08 safety evidence only.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-api-cli-entry`: `task run` accepts lifecycle owner-lock guard override arguments.
- `tdx-task-management`: task preset execution preserves and forwards lifecycle owner-lock guard options for PingAn trade tasks.
- `tdx-function-tree-registry`: D-07/D-08 register preset/run owner-lock guard forwarding without status promotion.

## Impact

- Code: `tdxquant/cli.py`, `FUNCTION_TREE.md`.
- Tests: task preset/run CLI parser/dispatch tests and FUNCTION_TREE registry tests.
- No default behavior change; no lifecycle process control, lock acquisition/release, broker readiness, live/manual acceptance, or workflow-builder semantics are introduced.
