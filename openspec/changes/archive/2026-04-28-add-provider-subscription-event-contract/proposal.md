## Why

`subscription-watch` 已经落地了第一版 `JSONL` 事件流，但当前事件 schema 仍然只存在于 task 文档和 task 内部实现里，还没有被正式提炼成独立的 provider-level contract。这会让上层项目难以把事件协议视为稳定边界，也会让后续接入 HTTP/SSE 或 replay fixture 时缺少一个可复用的统一定义。

## What Changes

- Introduce a dedicated provider-facing subscription event contract document and spec for normalized quote-update event rows.
- Extract subscription event normalization into a shared helper module instead of keeping the schema logic embedded only inside the task implementation.
- Make `subscription-watch` explicitly emit rows that conform to the provider-level subscription event contract.
- Update roadmap and integration references so upstream systems can treat the event row schema as a stable boundary independent from the task transport.

## Capabilities

### New Capabilities
- `tdx-provider-subscription-event-contract`: Stable provider-facing event-row contract for subscription quote updates.

### Modified Capabilities
- `tdx-task-subscription-watch`: Require `subscription-watch` to emit normalized rows that conform to the provider-level subscription event contract.

## Impact

- Affected code:
  - new shared subscription event contract helper module
  - `tdxquant/api/task.py`
- Affected tests:
  - shared contract normalization tests
  - task integration tests for event row output
- Affected docs:
  - provider subscription event contract documentation
  - roadmap / function map / integration references
- Compatibility:
  - no new runtime entrypoint is introduced
  - current `subscription-watch` artifact shape remains stable while moving to a formal shared contract definition
