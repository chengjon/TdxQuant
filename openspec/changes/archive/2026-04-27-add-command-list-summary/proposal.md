## Why

当前 `catalog list` 已经能列 entry、bundle、label 过滤，但输出仍然偏“诊断化”：

- 信息字段较多，日常扫一眼不够快
- 排序只是简单按名字，不够贴近日常优先级

对高频使用来说，入口发现本身也需要一个更短、更稳定的视图。

## What Changes

- 为 `catalog list` 增加可选的 `summary` 输出视图。
- 为 `catalog list` 增加更稳定的排序方式，优先按标签和名称提供一致结果。
- 保持默认详细列表兼容。
- 补充测试与文档。

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`: 增强 catalog list 的发现性输出

### New Capabilities

None.

## Impact

- 影响 `tdxquant/cli.py`、catalog list 测试与使用文档。
- 不修改 `run` / `plan` / `task` / `report` / `trade` 的执行行为。
