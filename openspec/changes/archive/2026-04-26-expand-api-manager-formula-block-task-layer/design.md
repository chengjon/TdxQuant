## Context

当前 API 管理层已经有明确的第一阶段落地成果：

- `context.py` 负责 profile 和 timing
- `market.py` 负责行情查询
- `meta.py` 负责静态列表和板块成分查询
- `manager.py` 负责统一元数据附加和顶层调用门面
- `api` 二级 CLI 已覆盖 MVP 范围

但 `runtime/TdxQuant_API_MVP_Compatibility_Notes.md` 也已经明确，本次 MVP 刻意保留了以下能力在旧入口：

- `send_user_block`
- 全部 formula 系列命令
- `task` 场景层

用户当前希望继续推进的方向，与 [docs/TdxQuant_API_System_Plan.md](/opt/iflow/TdxQuant/docs/TdxQuant_API_System_Plan.md:1) 第二阶段规划一致：

- 把 `formula / block` 纳入新的 manager 层
- 建立 `task` 层，提供稳定日常入口

## Goals / Non-Goals

**Goals**

- 让 `TdxApiManager` 具备完整业务域轮廓：`market`、`meta`、`formula`、`block`
- 为 `formula` 和 `block` 建立与现有 `market/meta` 一致的无状态 domain 封装
- 定义 task 层与 manager 层之间的清晰边界
- 为未来 `api` / `task` 双二级 CLI 做结构预留

**Non-Goals**

- 本次不把桌面自动化交易纳入 task 默认场景
- 本次不废弃旧公式命令或旧 block 命令
- 本次不引入长连接复用或大规模底层 bridge 重构
- 本次不把 task 层做成万能业务逻辑堆放点

## Decisions

### 1. `TdxApiManager` 扩展为四域结构

第二阶段完成后的 manager 结构应为：

- `manager.market`
- `manager.meta`
- `manager.formula`
- `manager.block`

这意味着后续代码层应新增：

- `tdxquant/api/formula.py`
- `tdxquant/api/block.py`

二者与 MVP 域保持同样原则：

- domain 模块无状态
- 只做参数透传与轻量整理
- 不读取 profile 文件
- 不承担 task 组合逻辑

### 2. `formula` 域承接现有 bridge 公式能力，但保持运行时准备动作显式

当前公式相关 bridge 能力覆盖：

- `formula_format_data`
- `formula_set_data`
- `formula_set_data_info`
- `formula_get_data`
- `formula_zb`
- `formula_xg`
- `formula_exp`
- `formula_process_mul_xg`
- `formula_process_mul_zb`

设计上不应把所有公式前置准备都隐式塞进一个单次调用里。更合理的分层是：

- `manager.formula` 继续暴露原子能力
- task 层在需要时编排“准备数据 -> 执行公式 -> 整理输出”

这样既保留原子可控性，也能在 task 层获得稳定日常入口。

### 3. `block` 域应承接 `send_user_block`，但保持写操作边界清晰

`send_user_block` 并不是只读元数据查询，因此不应塞进 `meta`。第二阶段应正式定义 `block` 域，用于承载：

- 自选股/自定义板块写入
- 后续可能的板块管理动作

在 manager 侧表现为：

- `manager.block.send_user_block(...)`

这样可以把读写边界从一开始就分清：

- `meta` 负责只读静态资料
- `block` 负责用户板块相关写操作

### 4. `task` 层是 manager 之上的场景编排层，不是第五个原子业务域

task 层的价值不在于新增底层能力，而在于固定高频场景。例如：

- 板块研究：取 sector 成分 + 批量行情 + 导出
- 公式扫描：准备公式数据 + 批量公式计算 + 汇总结果
- 日常盯盘：自选股刷新 + 快照整理
- 环境运维：缓存刷新 + 健康检查 + 基础连通性输出

因此 task 层应遵循：

- 只调用 manager 暴露的原子域接口
- 不直接调用 `bridge.py`
- 不重新实现底层错误封装
- 输出更面向日常使用的稳定结果结构

### 5. CLI 顶层结构应演进为 `api` + `task` 双入口

第二阶段之后的 CLI 方向应当是：

- `tdxquant api ...`
  - 面向原子能力
  - 适合脚本和精细控制
- `tdxquant task ...`
  - 面向稳定场景
  - 适合日常高频使用

现有扁平命令保留兼容，作为迁移期入口。

### 6. `task` 层应支持 profile，但 profile 粒度与 API 层不同

API manager 的 profile 主要偏向单次调用默认参数，例如：

- 字段列表
- list_type
- refresh_cache 默认值

task 层 profile 则更偏向场景，例如：

- 输出路径
- 导出格式
- 批量分页大小
- 默认字段组合
- 公式执行模式

因此推荐后续分开管理：

- `runtime/api-profiles.json`
- `runtime/task-profiles.json`

task 层调用内部仍可向 `TdxApiManager(profile=...)` 传入或转换成原子 profile。

## Risks / Trade-offs

- [`formula` 能力存在显式准备步骤] → 如果 task 层过度隐藏准备过程，容易削弱可诊断性，因此应保留原子入口。
- [`block` 是写操作] → 需要在 manager 和 CLI 上持续区分读写风险，避免误认为它与 `meta` 等价。
- [task 层容易膨胀成杂项集合] → 必须限制 task 只承载稳定高频流程，不承载一次性脚本逻辑。
- [新旧 CLI 会并存一段时间] → 需要在规格里明确兼容期，而不是强推一次性迁移。
- [API profile 与 task profile 语义不同] → 若混在一个文件里，后续会迅速失控，因此建议分层。

## Migration Plan

1. 先增加 `formula` / `block` domain 和 manager 代理，补齐 API 四域结构。
2. 再把 `api` 二级命令扩到 `formula / block` 范围，并保留旧扁平命令兼容。
3. 然后新增 `task` 层骨架与首批稳定场景。
4. 最后再补 `task` 二级 CLI 和 task profile。

## Open Questions

- `formula_format_data` 应保留在 `formula` 域，还是放入更底层的 task 辅助工具？
- `task` 第一批是否先只做只读场景，还是允许包含 `block` 写操作？
- `task` 输出是否统一为 JSON 结果，再按需附加 CSV/文件导出？
- `task` 是否直接复用 `TdxApiManager`，还是建立 `TdxTaskManager` 作为显式编排门面？
