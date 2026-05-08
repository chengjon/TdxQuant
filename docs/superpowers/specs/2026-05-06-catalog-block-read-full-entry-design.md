# Catalog Block Read Full Entry Design

## Context

当前 `block` 读侧已经具备稳定层级：

- provider capability
  - `block.read_watchlist_snapshot(...)`
- task entries
  - `task block-read-watchlist`
  - `task block-read-full`
  - `task block-read-watchlist-export`
- task presets
  - `task run --preset read-zxg-full`
  - `task run --preset export-zxg-watchlist`

同时，catalog 基础设施已经存在并可工作：

- catalog registry 文件：
  - `runtime/command-catalog.json`
- catalog source 校验：
  - `tdxquant/catalog.py:resolve_command_catalog_entry(...)`
- CLI 已支持：
  - `catalog list`
  - `catalog list --entry <name>`
  - `catalog plan --entry <name>`
  - `catalog run --entry <name>`

另外，catalog 里已经有一条完全同类的 task-source preset-backed 先例：

- `export-zxg-watchlist`
  - `source = "task"`
  - `preset = "export-zxg-watchlist"`

因此，这一包的真实缺口不是“新建一套 catalog schema 或 catalog 执行模型”，而是：

- 为 `block-read-full` 新增一条 **兼容现有 schema** 的 catalog entry
- 让现有 `catalog list / plan / run` 能发现并触发它

## Goals

- 让 catalog 能发现 `read-zxg-full` 这条 preset-backed `block-read-full` 入口。
- 继续复用现有 catalog schema 和 preset dispatch 逻辑。
- 验证现有：
  - `catalog list`
  - `catalog list --entry`
  - `catalog plan --entry`
  - `catalog run --entry`
  对该新 entry 的端到端可用性。

## Non-Goals

- 不新增 catalog schema
- 不新增 `catalog show`
- 不新增 catalog 内联参数输入
- 不做 preset create / edit / delete
- 不做新的 provider capability
- 不做新的 report / export 格式
- 不做上层系统写回

## Decision 1: Reuse the existing catalog schema exactly

V1 明确选择**复用现有 schema**，不做 schema 迁移。

现有 `runtime/command-catalog.json` entry 形态要求：

- `source`
- `preset`
- `description`
- `labels`

并且：

- `source` 必须属于 `SUPPORTED_COMMAND_CATALOG_SOURCES`
- 当前允许值为：
  - `"report"`
  - `"task"`
  - `"trade"`

因此，`block-read-full` 的 catalog 接入必须写成一条 **task-source preset-backed entry**，而不是引入新的：

- `entry_id`
- `kind`
- `preset_name`
- `summary`

之类字段。

### Example entry

```json
{
  "read-zxg-full": {
    "source": "task",
    "preset": "read-zxg-full",
    "description": "Read full diagnostics view for ZXG.",
    "labels": ["task", "block", "watchlist", "diagnostics"]
  }
}
```

## Decision 2: Catalog remains a preset view layer

V1 的 catalog entry 只是 preset 的可发现视图：

- `export-zxg-watchlist` 已经验证了这种 task-source preset-backed pattern
- `read-zxg-full` 继续复用同一模式

- `catalog run --entry read-zxg-full`
  - 最终仍委派到：
    - `task run --preset read-zxg-full`
- `catalog plan --entry read-zxg-full`
  - 继续复用现有 preset 解析与 namespace 展示逻辑

也就是说：

- catalog 不重新承担参数建模
- catalog 不直接执行 `block-read-full`
- catalog 不复制 preset defaults

## Decision 3: V1 does not add `catalog show`

当前 CLI 已经有现成功能：

- `catalog list --entry <name>`

它已经能承担“查看单条 entry”的角色。

因此，V1 不新增 `show` 子命令。  
单条 entry 的查看语义统一复用：

- `catalog list --entry read-zxg-full`

## Decision 4: V1 explicitly includes `catalog plan`

现有 `catalog plan --entry <name>` 已经是最有价值的诊断入口之一，因为它能展示 preset 解析后的 namespace。

因此，V1 明确支持：

- `catalog list`
- `catalog list --entry <name>`
- `catalog plan --entry <name>`
- `catalog run --entry <name>`

其中 `plan` 不需要新实现，只需要确保新 entry 能被现有流程正确消费。

## Decision 5: Do not inline preset parameters into catalog entries

V1 不在 `command-catalog.json` 里内联：

- `block_code`

原因：

- 这个值已经存在于 `runtime/task-presets.json`
- 在 catalog entry 中重复一份会造成双写与漂移

如果需要查看解析后的默认值，应通过现有：

- `catalog plan --entry read-zxg-full`

来查看，而不是在 registry 里静态重复存储。

## Error semantics

V1 的错误语义继续复用现有 catalog / preset 校验：

- entry 不存在
  - 稳定失败
- entry 缺少 `source` 或 `preset`
  - 稳定失败
- `source` 不在允许集合中
  - 稳定失败
- entry 对应 preset 丢失
  - 稳定失败
- `catalog run` 期间底层 task 失败
  - 直接返回底层 task result
  - catalog 层不做二次翻译

这一包不新增新的 catalog 错误模型。

## Implementation surface

V1 只建议动这些具体位置：

- `runtime/command-catalog.json`
  - 新增一条 task-source entry
- `tests/test_api_cli.py`
  - 补 `catalog list / list --entry / plan / run` 对该 entry 的 focused regression

V1 明确**不需要新增 usage doc**：

- `catalog list --entry read-zxg-full`
- `catalog plan --entry read-zxg-full`

已经足够自描述这条 entry 的 source、preset 和解析结果。

原则上**不需要修改**：

- `tdxquant/catalog.py`
- `tdxquant/cli.py` 里的 catalog dispatch 逻辑
- provider contract
- task `block-read-full` logic
- preset schema

## Test boundaries

第一版 focused tests 只覆盖这条增量：

- `catalog list` 能看到 `read-zxg-full`
  - 且是在**未过滤的默认 entry 列表**中可见
- `catalog list --entry read-zxg-full` 能返回该 entry
- `catalog plan --entry read-zxg-full` 能展示解析后的 preset args
  - 至少断言 `resolved_args` 中包含正确的：
    - `block_code`
- `catalog run --entry read-zxg-full` 能委派到现有：
  - `task run --preset read-zxg-full`

不要求：

- 新增 catalog 子命令测试
- 新增 catalog schema 迁移测试
- provider / task 深层逻辑重复测试

## Rationale

这条设计的核心是：

**V1 不是“设计 block-read-full 的新 catalog 功能”，而是“把现有 block-read-full preset 接到现有 catalog 上”。**

因此最小且正确的增量是：

1. 在 `command-catalog.json` 增一条兼容现有 schema 的 task entry
2. 证明现有 `catalog list / plan / run` 对它可用
3. 不重新设计 schema，不复制 preset 参数，不新增 catalog 子命令

## Naming note

当前第一条 entry 采用：

- `read-zxg-full`

如果后续继续增加其他 block full-diagnostics catalog entries，建议保持同一命名模式：

- `read-<block>-full`

这一点在 V1 不作为强约束，只作为后续扩展时的连续性约定。
