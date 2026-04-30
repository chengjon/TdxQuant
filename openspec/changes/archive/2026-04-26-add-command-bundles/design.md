## Context

当前统一入口已经分为两层：

- `task` / `report` / `trade`: 稳定 workflow 与命令级 preset
- `catalog`: 跨命令组的单条日常入口索引

缺口在于：`catalog` 目前仍然是一条命令对应一条 workflow，无法表达“固定顺序执行 2-3 条已存在命令”的日常流程。

## Goals / Non-Goals

**Goals:**

- 允许通过一个命名化 bundle 顺序执行多个既有 catalog entry。
- bundle 仍然只复用既有 entry 对应的 `task/report/trade` preset 分发链。
- 保证显式 CLI 参数继续覆盖 bundle step 默认值。
- 保持 `catalog run --entry ...` 完全兼容。

**Non-Goals:**

- 不把 bundle 写成新的 manager 或 task workflow。
- 不支持条件分支、循环、并行执行或跨步骤变量引用。
- 不把 top-level `--output` 自动拆分成多份 step 输出文件。
- 不合并 `command-catalog.json` 与新的 bundle 配置文件。

## Decisions

### 1. 使用独立 `runtime/command-bundles.json`

bundle 与单条 entry 语义不同：

- entry: 指向一个 preset
- bundle: 顺序引用多个 entry

因此本轮新增独立的 `runtime/command-bundles.json`，避免把 `command-catalog.json` 混成两种结构。

bundle 结构：

```json
{
  "refresh-review": {
    "description": "先刷新环境，再看最近台账摘要。",
    "steps": [
      {"entry": "refresh-env"},
      {"entry": "recent-ledger", "options": {"limit": 10}}
    ]
  }
}
```

每个 step 允许声明：

- `entry`: 既有 catalog entry 名称
- `description`: 可选说明
- `options`: 可选默认参数字典

### 2. 在现有 `catalog` 命令组上做兼容扩展

不新增新的顶层命令组，而是扩展现有 `catalog`：

- `catalog list`
- `catalog list --kind bundle`
- `catalog list --kind all`
- `catalog list --bundle <name>`
- `catalog run --entry <name>`
- `catalog run --bundle <name>`

这样调用模型仍然统一保持为“catalog 负责发现与执行”，避免再多一层命令名。

### 3. bundle step 只复用既有单条 entry 分发逻辑

bundle 不直接调用 manager，也不重新解释业务参数。执行策略：

1. 解析 bundle
2. 逐步解析 step 引用的 catalog entry
3. 用 step `options` 补齐当前 CLI 参数中的空值
4. 复用现有 `catalog entry -> task/report/trade` 分发逻辑执行
5. 任一步失败即停止后续 step

这样 bundle 只是“catalog 的组合层”，不是第五套 workflow。

### 4. top-level `--output` 仅写 bundle 汇总结果

bundle 场景下，如果仍把同一个 `--output` 透传给每个 step，会导致多步结果互相覆盖。因此约定：

- `catalog run --bundle ... --output file.json`
  - 只写整体 bundle 汇总结果
- 各 step 如需单独导出文件，应通过底层 preset 默认值或 step `options` 指向其自身输出参数

### 5. 汇总结果保留 step 粒度信息

bundle 执行结果应返回：

- bundle 元数据
- 每个 step 的 entry/source/preset
- 每个 step 的 `ok/code/message`
- 每个 step 的完整 `result`
- 失败时的 `failed_step`
- 汇总 timing

如果 bundle 中出现 trade-backed step，则同时暴露首个可解析合同号，保持后续日志链路可继续利用。

## Risks / Trade-offs

- [参数面继续偏宽] → 这是对现有 catalog 联合参数面的延续，bundle 仍不解释业务参数。
- [bundle 结果体较大] → 这是保留逐 step 排障信息的代价，日常诊断收益更高。
- [step 输出文件策略有限] → 本轮先只保证顶层聚合输出稳定，复杂多文件编排后续再做。
