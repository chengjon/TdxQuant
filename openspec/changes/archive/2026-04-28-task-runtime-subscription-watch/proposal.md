## Why

当前项目已经具备持久 `runtime subscription session`，但它还停留在 Python 级原子能力，没有形成一个适合日常运行、也适合上层项目先用文件协议联调的稳定入口。现在需要补一个前台长驻 `subscription-watch` task，把实时订阅治理、JSONL 事件落盘和结束态摘要收口为首个可直接消费的订阅 workflow。

## What Changes

- Add a stable `task subscription-watch` workflow above `manager.runtime.open_subscription_session()`.
- Normalize subscription callback payloads into machine-readable event rows and append them to `JSONL` and `CSV` artifacts.
- Write a structured status artifact that records run state, stop reason, event counts, and output paths.
- Support explicit bounded-run controls such as `max-events` and `max-seconds`, while preserving foreground `Ctrl+C` graceful shutdown behavior.
- Keep scope intentionally limited to a foreground task; no daemon, no process control plane, and no `catalog`/preset expansion in this package.

## Capabilities

### New Capabilities
- `tdx-task-subscription-watch`: Stable foreground runtime subscription watch workflow with normalized event artifacts and completion summary.

### Modified Capabilities
- `tdx-task-management`: Add a stable task-layer workflow that owns a runtime subscription session and exposes it through `TdxTaskManager` and `task subscription-watch`.

## Impact

- Affected code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `runtime/task-profiles.json`
- Affected tests:
  - task manager workflow tests
  - task CLI parser and dispatch tests
- Affected docs:
  - subscription-watch task contract documentation
  - roadmap / function map references
- Affected behavior:
  - introduces a new long-running foreground task with structured `JSONL` / `CSV` / status artifacts
