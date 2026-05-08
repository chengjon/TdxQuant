# Task Block Sync Design

Date: 2026-05-03
Topic: `task-block-sync`
Status: Draft for review

## Context

截至 `2026-05-03`，项目已经补齐 provider-level `block sync` 主线：

- Python：`TdxApiManager.block.sync_watchlist(...)`
- nested CLI：`tdxquant api block-sync ...`
- flat CLI：`tdxquant tdx-block-sync ...`
- replay fixtures、discovery metadata、mutation governance、audit artifact 都已经稳定

但 `task / report / catalog` 这一层里，`block sync` 还没有一个正式的日常场景入口。  
当前最缺的不是新的底层同步协议，而是一个**不重新定义 contract 的 task 入口**。

## Goal

把 provider-level `block.sync_watchlist` 提升成一个稳定的 task 场景入口：

- `TdxTaskManager.block_sync(...)`
- `tdxquant task block-sync ...`

并保持它是一个**薄包装**：

- 直接消费现有 provider capability
- 直接返回现有 sync summary / governance result / audit artifact
- 不新增 task-only schema

## Non-Goals

- 不做 CSV / JSON / watchlist 文件导入
- 不做 `task preset`
- 不做 `catalog` entry / bundle
- 不做 task 专属 run artifact
- 不做 report 层派生
- 不改变 provider-level `block.sync_watchlist` contract
- 不扩展到 `TongDaXin block -> 上层 watchlist` 双向同步

## Approaches Considered

### A. Thin task wrapper

新增 `task block-sync`，直接把 task 参数透传给 `manager.block.sync_watchlist(...)`，返回值沿用底层 provider result。

优点：

- 范围最稳
- 不会重新定义底层 contract
- 最符合 `task` 作为日常入口而不是新治理层的定位

缺点：

- 第一版没有 preset / catalog 便捷层

### B. Task + preset

在 A 的基础上追加 `task preset`，把常用 block code / mode / create_if_missing 做成配置化入口。

优点：

- 高频日常操作更顺手

缺点：

- scope 明显变胖
- 会让“先收 task contract”与“再做 productization”混在一包

### C. Task + preset + catalog

一次把 `task block-sync`、task preset、catalog entry/bundle 都做齐。

优点：

- 日常入口最完整

缺点：

- 容易让 `catalog` 反向主导底层
- 明显超出当前 change 的合理范围

## Chosen Approach

选择 **A. Thin task wrapper**。

原因：

- provider-level `block.sync_watchlist` 已经稳定，task 层此时最该做的是“复用”，而不是“重新发明”
- `task` 在当前架构里是日常入口层，不是新的协议层
- preset / catalog 是否值得做，应该建立在 task 入口已经证明高频的基础上

## Design

### 1. Public Entry Points

第一版新增两个入口：

- Python：
  - `TdxTaskManager.block_sync(...)`
- CLI：
  - `tdxquant task block-sync ...`

两者都只编排到：

- `TdxApiManager.block.sync_watchlist(...)`

不新增新的 bridge 调用路径，不允许 task 层绕开 manager。

`strategy_path` 继续沿用现有 `TdxTaskManager(..., strategy_path=...)` / task profile 的构造方式传入 `TdxApiManager`，不额外成为 `block_sync(...)` 方法签名里的显式参数。

### 2. Request Shape

第一版 task 层只接受显式参数，不支持文件导入。

输入字段：

- `block_code`
- `symbols`
- `mode`
  - `replace` 默认
  - `merge`
- `create_if_missing`
  - 默认 `false`
- `dry_run`
  - 默认 `false`
- `mutation_key`
  - 可选
- `audit_dir`
  - 可选，透传到底层
- `show`
  - 透传到底层，默认保持 `true`

语义：

- Python API 使用 `symbols`，与 provider-level `block.sync_watchlist(...)` 保持一致
- CLI 继续保留 repeatable `--stock` 参数，解析后映射到 task 层的 `symbols`
- task 层不负责从文件解析 watchlist
- 代码规范化、去重、diff 计算、治理决策都继续由 provider-level `block.sync_watchlist` 负责
- `audit_dir` 只是 passthrough；如果省略，继续使用底层默认审计目录
- `show` 第一版继续保持 `true`，与 `api block-sync` / `tdx-block-sync` / provider-level 默认行为一致，避免 task 入口单独偏离现有桌面交互语义

### 3. Response Shape

task 层返回值直接沿用 provider-level `block sync` 结果结构，并按现有 task 约定补齐 task metadata：

- `success/code/message`
- `data.sync`
- `data.block_mutation`
- `artifacts`
- `data.task`
- `data.task_profile`
- `data.timing`

也就是说，`TdxTaskManager.block_sync(...)` 应继续走现有 task wrapper 模式：

- `_capture_task_timing("task.block_sync", ...)`
- `_attach_task_metadata(..., task_name="block_sync", timing=timing)`

而不是做一个不带 task metadata 的例外实现。  
这仍然是“薄包装”，因为 task 层只是附加统一 task 运行元数据，不改写底层 sync/governance 结果结构。

这意味着：

- `replace` 已一致 -> `noop`
- `merge` 已全部包含 -> `noop`
- `dry_run=true` -> 返回完整计划摘要，但不真实写入
- `create_if_missing=false` 且目标板块不存在 -> 底层稳定 `rejected`

全部保持 provider-level 语义不变。

### 4. Error Semantics

错误语义完全跟底层 provider capability 对齐：

- `noop` 仍然是成功
- `rejected` 仍然是稳定业务拒绝
- `failed` 仍然是执行失败
- `mutation_key` 冲突仍然是底层稳定拒绝

task 层不再把这些翻译成 task-specific 状态，不引入：

- “task success but business fail”
- “task planned but provider not planned”

这条规则的目的是让上层对 `api block-sync` 和 `task block-sync` 使用同一套 machine contract。

### 5. CLI Contract

CLI `task block-sync` 是 task 层显式参数入口，不是 preset 或 catalog 包装。

示意：

```bash
python -m tdxquant.cli task block-sync \
  --block-code ZXG \
  --stock 000001.SZ \
  --stock 600519.SH \
  --mode replace \
  --create-if-missing \
  --dry-run
```

第一版不支持：

- `--file`
- `--preset`
- `catalog run block-sync-*`

这样能确保 CLI 只是 task contract 的直接映射，不引入多层入口耦合。

注册方式继续沿用现有 task 子命令模式：

- `task_subparsers.add_parser("block-sync")`
- `--stock` 采用 repeatable `action="append"`
- 复用 `_add_block_sync_arguments(...)`
- 再复用 `_add_task_common_arguments(...)`

### 6. Testing

第一版测试只覆盖 task 层的“薄包装正确性”，不重复验证底层 sync orchestration。

建议至少补：

#### Manager / task tests

- `TdxTaskManager.block_sync(...)` 会调用 `manager.block.sync_watchlist(...)`
- task 层不会偷偷改写底层 result

#### CLI tests

- parser：
  - `task block-sync --block-code ... --stock ...`
- dispatch：
  - CLI 调到了 `TdxTaskManager.block_sync(...)`
- JSON contract：
  - stdout 直接反映底层 result

#### Focused task-layer tests only

不在 task 层重复测试：

- diff 计算
- `replace/merge`
- `create_if_missing`
- `mutation_key` 语义

这些继续由现有 provider-level `block sync` 测试负责。

### 7. Documentation

这包完成后只需要更新：

- `runtime/TdxQuant_Task_Layer_Usage.md`
- `docs/TdxQuant_Project_Function_Map.md`
- `docs/TdxQuant_Next_Steps.md`

可选再补一个 task 层章节到 `block sync` 相关文档，但不需要新增 report/catalog 文档。

## Risks

### 1. Task 层无意中重新定义底层 contract

规避方式：

- task 只做参数收口和调用编排
- 返回值直接沿用 provider-level result

### 2. 把文件导入和同步治理混在一包

规避方式：

- 第一版只支持显式 `--stock`
- 文件导入单独留到后续场景 productization change

### 3. 过早引入 preset / catalog

规避方式：

- 第一版只做 task
- 高频使用验证后，再单独开 preset / catalog 收口包

## Open Questions

无。第一版范围已经明确：

- 只做 `task block-sync`
- 只支持显式参数
- 只做薄包装
