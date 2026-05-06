## Context

现有 block read full 链路已经具备：

- task workflow:
  - `task block-read-full`
- task preset:
  - `read-zxg-full`

同时，现有 catalog 基础设施已经具备：

- `runtime/command-catalog.json`
- `tdxquant/catalog.py:resolve_command_catalog_entry(...)`
- `catalog list`
- `catalog list --entry <name>`
- `catalog plan --entry <name>`
- `catalog run --entry <name>`

因此，这条 change 的工作不是设计新的 catalog 模型，而是把 `read-zxg-full` 接进现有 catalog。

## Goals / Non-Goals

**Goals**

- 正式定义 `read-zxg-full` 为稳定 catalog entry。
- 明确该 entry 复用现有 command-catalog schema。
- 明确 `catalog plan/run` 继续委派到既有 preset dispatch 逻辑。

**Non-Goals**

- 不修改 catalog schema
- 不新增 `catalog show`
- 不新增 inline 参数输入
- 不修改 provider/task `block-read-full` contract

## Decisions

### 1. Reuse the existing command-catalog schema exactly

第一版 entry 必须继续使用现有 schema：

- `source`
- `preset`
- `description`
- `labels`

并满足：

- `source == "task"`
- `preset == "read-zxg-full"`

不引入新的：

- `entry_id`
- `kind`
- `summary`
- `preset_name`

### 2. Catalog remains a preset-backed view layer

`catalog` 对这条 entry 的职责只有：

- 发现它
- 展示它
- 通过现有 `task run --preset ...` 路径触发它

因此：

- `catalog run --entry read-zxg-full`
  继续等价于：
  - `task run --preset read-zxg-full`
- `catalog plan --entry read-zxg-full`
  继续展示解析后的 preset namespace

### 3. V1 includes list, single-entry inspection, plan, and run

V1 显式要求这四条现有路径可用：

- `catalog list`
- `catalog list --entry read-zxg-full`
- `catalog plan --entry read-zxg-full`
- `catalog run --entry read-zxg-full`

不新增新的 catalog subcommand。

## Risks / Trade-offs

- [在 catalog entry 中重复存 preset 参数] → 通过只存 `source/preset/description/labels` 规避。
- [为单条 entry 引入新 schema] → 通过继续复用现有 loader/validator 规避。
- [catalog 层重写底层 task 结果] → 通过继续复用现有 dispatch 规避。

## Migration Plan

1. 在 `runtime/command-catalog.json` 新增 task-source entry。
2. 用 focused CLI tests 锁住 list/single-entry/plan/run 四条现有路径。
3. 将这条行为写回 `tdx-command-catalog` 主 spec。
4. 同步修正文档里“仍未 catalog-backed”的滞后描述。
5. 归档 change。

## Open Questions

- 无。V1 只 formalize 最小增量 catalog entry。
