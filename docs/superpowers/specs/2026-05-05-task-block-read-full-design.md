# Task Block Read Full Design

Date: 2026-05-05
Topic: `task-block-read-full`
Status: Draft for review

## Context

当前 block 读侧已经有两条稳定主线：

- provider-level canonical read：
  - `block.read_watchlist_snapshot(...)`
- task-level daily entry：
  - `task block-read-watchlist`
  - `task block-read-watchlist-export`

其中：

- `block.read_watchlist_snapshot(...)`
  已经稳定返回标准化 `snapshot`
- `task block-read-watchlist`
  是它的薄包装
- `task block-read-watchlist-export`
  是在成功 snapshot 基础上的单文件 JSON 导出型 task

但还缺一个更适合**读侧日常排查 / 诊断 / 人工检查**的高层 task：

- 不只是返回标准化 snapshot
- 还要把 snapshot 已经包含的诊断信息，以更直接的 task 视图整理出来
- 同时不引入新的 provider 能力，不做第二次 raw query，不做写逻辑

这就是 `task block-read-full` 的定位。

## Goal

新增一个稳定的高层读侧 task：

- Python：
  - `TdxTaskManager.block_read_full(...)`
- CLI：
  - `tdxquant task block-read-full --block-code ZXG`

第一版它应当：

- 只读取**单个** `block_code`
- 只基于现有：
  - `manager.block.read_watchlist_snapshot(...)`
- 保留底层 `data.snapshot`
- 追加一个 task-level enriched 读视图：
  - `data.read_full`

它不是新的 provider contract，也不是导出任务，也不是批量/后台/分布式能力。

## Non-Goals

- 不做多 block 批量读取
- 不做文件导出
- 不做后台服务
- 不做分布式
- 不做 raw rows 返回
- 不做第二次 `meta.sector_stocks(...)` 读取
- 不做任何写逻辑
- 不做新的 provider capability

## Approaches Considered

### A. Thin full task on top of canonical snapshot

新增 `task block-read-full`，只调用：

- `manager.block.read_watchlist_snapshot(...)`

成功时保留：

- `data.snapshot`

并追加：

- `data.read_full`

优点：

- 改动最小
- 不复制 provider contract
- 最符合“高层场景，但不做复杂转换”的边界

缺点：

- `full` 是 task-level enriched view，不是新的 provider capability

### B. Re-read raw sector data inside the task

在 task 层除了 snapshot 之外，再额外读取一次：

- `meta.sector_stocks(...)`

然后合并生成更厚的 full result。

优点：

- 可以附带更多 raw read context

缺点：

- 读路径变成两次底层调用
- 会把 task 变成新的数据整合层
- 明显超出你当前锁定的边界

### C. Add `--full` to existing `task block-read-watchlist`

不新增命令，而是在现有 task 上加：

- `--full`

优点：

- 入口更少

缺点：

- 会把“薄包装”和“高层 enriched 视图”混进同一个命令
- 错误语义和返回形态更容易变脏

## Chosen Approach

选择 **A. Thin full task on top of canonical snapshot**。

原因：

- 现有 canonical read contract 已经稳定
- 当前缺的是高层场景入口，不是新的读协议
- task 层最该做的是“整理与附加视图”，不是重新发明一条 block read provider

## Design

### 1. Public Entry Points

新增两个入口：

- Python：
  - `TdxTaskManager.block_read_full(...)`
- CLI：
  - `tdxquant task block-read-full --block-code ZXG`

两者都只编排到：

- `TdxApiManager.block.read_watchlist_snapshot(...)`

不新增新的 bridge 调用路径，不允许 task 层绕开 manager。

### 2. Request Shape

第一版输入非常克制，只接受：

- `block_code`

不支持：

- 多个 `block_code`
- `--output`
- `--format`
- 文件导入
- 任何写入参数

也就是说，这是一个**单次单 block 的高层读 task**。

### 3. Response Shape

顶层继续沿用现有 `Result` envelope、manager metadata 与 task metadata 约定。

成功时保留：

- `success/code/message`
- `data.snapshot`
- provider/manager metadata
  - `data.manager`
  - `data.api_profile`

并追加：

- `data.read_full`
- `data.task`
- `data.task_profile`
- `data.timing`

#### `data.snapshot`

继续作为 canonical machine contract，完全沿用：

- `block_code`
- `symbols`
- `symbol_count`
- `source`
- `source_metadata`

#### `data.read_full`

第一版只是一个**从成功 snapshot 直接派生**的 diagnostics summary，不引入 raw rows，也不再把 `snapshot` 字段做第二次平铺。

建议字段：

- `sector_name`
- `raw_member_count`
- `duplicate_count`
- `warnings_present`

语义：

- `sector_name`
  - 来自 `snapshot.source_metadata.sector_name`
- `raw_member_count`
  - 来自 `snapshot.source_metadata.raw_member_count`
- `duplicate_count`
  - 来自 `snapshot.source_metadata.duplicate_count`
- `warnings_present`
  - `len(warnings) > 0`

设计意图：

- `snapshot` 继续作为 source of truth
- `read_full` 只放 task-level diagnostics-oriented summary
- 调用方如果需要 canonical fields，应继续读取 `data.snapshot`

#### Degraded snapshot handling

`read_full` 的生成建立在 **snapshot 成功** 之上，但不要求 `source_metadata` 完全齐全。

第一版 fallback 规则：

- `snapshot` 成功且 `source_metadata` 缺少可选字段时
  - 仍生成 `data.read_full`
  - 对应字段设为 `None`
- `snapshot` 成功且 `symbols=[]`
  - 仍正常生成 `data.read_full`
  - `raw_member_count` / `duplicate_count` 继续按 snapshot 提供的值或 `None`
- 只有当底层 `read_watchlist_snapshot(...)` 本身失败时
  - 才不生成 `data.read_full`

### 4. Failure Semantics

如果：

- `manager.block.read_watchlist_snapshot(...)`
  本身失败

则 `task block-read-full`：

- 直接透传底层失败
- 只追加标准 task metadata
- **不**伪造 `data.read_full`
- 不转换 error code，也不 catch/re-raise 成新的 task-specific failure

这条规则的目的是避免出现：

- 失败结果
- 但又带着半套看似成功的 enriched read view

因此 `data.read_full` 只应存在于**成功 snapshot** 之上。

### 5. CLI Contract

CLI 第一版保持简单：

```bash
python -m tdxquant.cli task block-read-full --block-code ZXG
```

它不是：

- `task block-read-watchlist --full`

而是一个独立命令。这样可以保持：

- `block-read-watchlist`
  = thin snapshot wrapper
- `block-read-full`
  = high-level enriched read view

边界更清楚。

需要单独说明的是：

- 这条命令预计仍会复用 `_add_task_common_arguments(...)`
- 因此会继续带有通用：
  - `--output`

这里的 `--output` 语义仍然只是：

- 将整条命令的 JSON 结果写到文件

它**不是**：

- block read export 语义
- `data.snapshot` 单独导出语义

因此第一版“不支持 `--output`”的意思是：

- 不支持把它当作领域级导出参数
- 但不会移除现有通用 task JSON result output 能力

### 6. Testing

第一版只补 focused task-layer tests，不重复验证底层 provider canonical read。

建议至少覆盖：

#### Manager / task

- `TdxTaskManager.block_read_full(...)` 调用：
  - `manager.block.read_watchlist_snapshot(...)`
- 成功时保留 `data.snapshot`
- 成功时生成 `data.read_full`
- 成功时：
  - `read_full.sector_name == snapshot.source_metadata.sector_name`
  - `read_full.raw_member_count == snapshot.source_metadata.raw_member_count`
  - `read_full.duplicate_count == snapshot.source_metadata.duplicate_count`
  - `read_full.warnings_present == (len(warnings) > 0)`
- snapshot 成功但 `source_metadata` 部分缺失时
  - `data.read_full` 仍生成
  - 缺失字段为 `None`
- 失败时不生成 `data.read_full`
- task metadata 仍按现有方式附加

#### CLI

- parser：
  - `task block-read-full --block-code ZXG`
- dispatch：
  - CLI 正确调用 `TdxTaskManager.block_read_full(...)`
- JSON contract：
  - 成功时输出保留 `data.snapshot` 并带 `data.read_full`
  - 失败时不输出 `data.read_full`

### 7. Preset stance

第一版不把 `block-read-full` 接进 task preset 体系。

也就是说：

- 不新增 `TASK_COMMAND_DEFAULT_PROFILES` 映射
- 不新增 `runtime/task-presets.json` entry

如果后续证明它是高频入口，再单独开一包做 preset / catalog productization。

## Error Handling Notes

第一版不新增 task-specific business error code。

也就是说：

- block 不存在
- invalid member
- snapshot read failure

这些都继续沿用底层：

- `block.read_watchlist_snapshot(...)`

的错误语义。

task 层不再做二次翻译。

## Rationale

这条设计的核心是：

- **provider 负责 canonical read contract**
- **task full 负责高层读侧视图整理**

它不该变成新的原始读取器、导出器、批处理器、或写回器。

第一版最正确的增量就是：

1. 新增独立 `task block-read-full`
2. 只依赖现有 `read_watchlist_snapshot(...)`
3. 成功时追加 `data.read_full`
4. 失败时不伪造 `data.read_full`
