# TdxQuant API MVP 实施方案 -- 结构化审核报告

> 审核对象：`runtime/TdxQuant_API_MVP_Implementation_Plan.md`
> 审核日期：2026-04-26

---

## 1. 整体评价

方案总体质量较高，方向正确，遵循了"底层不动、中间分层、上层统一"的低风险渐进策略。四层架构（bridge -> domain -> manager -> profile）职责划分清晰，与上位文档 `docs/TdxQuant_API_System_Plan.md` 的战略方向一致。开发顺序合理，验收标准明确。

但方案在若干关键细节上存在与现有代码的不一致，有一个严重的文件名冲突问题，以及一些边界遗漏需要补充。

---

## 2. 架构合理性

**[GOOD]** 分层设计清晰，符合关注点分离原则。

`bridge.py`（底层透传） -> `market.py` / `meta.py`（业务域封装） -> `manager.py`（统一调度门面） -> `api-profiles.json`（参数预设），每层职责单一，依赖方向单向向下，不构成循环。

**[GOOD]** 不替换、不废弃旧命令的策略正确。

现有 CLI 命令（约 40+ 个子命令）已经稳定运行，新 `api` 二级入口增量添加风险最低。

**[GOOD]** 数据流设计简洁。

```
CLI / Python 调用 -> TdxApiManager -> market/meta domain -> bridge.py -> tqcenter
```

这条链路没有多余层级，每一跳都有明确的存在理由。

**[INFO]** `TdxApiManager` 建议形态中属性式调用 `manager.market.snapshot(...)` 是合理设计，但实现时需注意每个域对象不应持有可变状态 -- 建议 `market` / `meta` 作为属性返回无状态的代理对象，或将方法注册为 class method / static callable。

---

## 3. 与现有代码一致性

**[CRITICAL] 文件名冲突：`tdxquant/api/runtime.py` vs `tdxquant/runtime.py`**

方案第 4 节目标结构新增 `tdxquant/api/runtime.py`，但项目中已存在 `tdxquant/runtime.py`（93 行），负责 Ping An Securities 运行时路径解析（`resolve_runtime()` 函数）。虽然路径不同（`api/runtime.py` 在子包内），但两个文件同名会导致：

1. 在同一项目中 `import` 时，开发者极易混淆 `from tdxquant.runtime import ...` 与 `from tdxquant.api.runtime import ...`。
2. IDE 跳转和代码搜索时增加认知负担。
3. `tdxquant/brokers/pingan.py:8` 已经在引用 `from ..runtime import resolve_runtime`。

**建议**：将新文件重命名为 `tdxquant/api/context.py` 或 `tdxquant/api/profile_helper.py`，避免与现有的 `tdxquant/runtime.py` 产生混淆。

**[WARNING] `send_user_block` 未纳入任何业务域**

方案 5.3 节 `market.py` 和 5.4 节 `meta.py` 的接口列表中均未包含 `send_user_block`（对应 `bridge.py:355-365`），该函数在 CLI 中也有对应命令 `tdx-send-user-block`（`cli.py:406-410`）。这个接口属于"自选/板块域"的写操作，但方案明确本阶段不做 `block.py`。然而方案也没有说明它在 MVP 阶段的处置策略 -- 是否暂时留在 `bridge.py` 不动、还是临时归入 `meta.py`。

**建议**：在方案第 9 节"本阶段不做的内容"中显式列出 `send_user_block` 的处置策略，例如"暂不纳入 manager，保留在 bridge.py 直接调用"。

**[WARNING] `formula` 系列接口（8 个函数）在 bridge.py 中已存在但方案完全未提及其 MVP 处置**

`bridge.py:368-513` 包含 8 个 formula 相关函数。方案第 9 节仅说"不拆 `formula.py`"，但未说明这些函数在新的 manager 体系中如何被调用 -- 如果新 CLI `api` 入口不覆盖它们，旧入口仍可使用，这一点需要明确写入方案以消除歧义。

**[INFO] `api/__init__.py` 当前使用 `from .bridge import *` 星号导出**

当前 `tdxquant/api/__init__.py:1-3` 的内容是：
```python
from .bridge import *  # noqa: F401,F403
```
方案未提及是否修改此文件。新增 `runtime.py`、`market.py`、`meta.py`、`manager.py` 后，应考虑是否在 `__init__.py` 中导出 `TdxApiManager` 等公共 API。建议方案补充此文件的变更说明。

**[GOOD] `DIRECTORY_PLAN.md` 已预见了 `market.py` / `meta.py` / `formula.py` / `block.py` 的拆分**

`tdxquant/DIRECTORY_PLAN.md:37-46` 明确记录了后续目录规划，包括"若 API 数量继续增长，再拆分为 `market.py`、`meta.py`、`formula.py`、`block.py`"。方案与现有规划完全一致。

---

## 4. 边界约束

**[GOOD]** 五条边界约束定义充分且合理：

1. 不重构桌面自动化交易路径
2. 不废弃扁平 CLI 命令
3. manager 不直接承担底层桥接
4. 本阶段不引入交易执行类 API
5. 本阶段不大规模拆空 `bridge.py`

这五条约束与上位文档 `TdxQuant_API_System_Plan.md` 第五节"关键边界约定"完全对齐。

**[WARNING] bridge.py 中 `_run_tq_call` 的连接初始化模式未被方案讨论**

`bridge.py:131-170` 中的 `_run_tq_call` 每次调用都会执行 `_init_tqcenter()` 和 `tq_class.close()`，即每次 API 调用都是"初始化 -> 执行 -> 关闭"的短连接模式。方案中 `runtime.py` 被定位为"顶层治理工具层，不是新的底层连接实现层"（方案 5.2 节），但上位文档第三节提到"连接复用"是 Manager 的核心职责之一。

如果未来要实现连接复用，那么 `bridge.py` 的 `_run_tq_call` 模式需要调整。方案应明确：MVP 阶段是否维持现有的短连接模式？如果维持，应在约束中显式声明。

**[WARNING] `refresh_cache` 归属 meta 域的理由牵强**

方案 5.4 节将 `refresh_cache` 归入 `meta.py`，理由是"当前最贴近日常只读查询准备动作"。但实际上 `refresh_cache` 是一个写操作（刷新市场缓存），放在只读查询域 `meta` 中语义不清。方案虽然提到"后续如果运行时动作增多，再迁入 runtime 域"，但考虑到新文件命名冲突问题（见上方 CRITICAL 项），不如在 MVP 阶段就将其作为 `manager` 的直接方法（`manager.refresh_cache()`），而不是勉强塞入 `meta`。

**[INFO] profile 与现有 `PINGAN_BUY_PROFILES` 的关系未说明**

`cli.py:88-137` 已有成熟的 profile 使用模式（`PINGAN_BUY_PROFILES` 字典，支持 `stable` / `balanced` / `fast` / `turbo` 四个预设），并且 `_build_pingan_buy_submit_options()` (`cli.py:710-715`) 实现了"profile + override"的合并逻辑。方案新增的 `api-profiles.json` 应说明是否复用此模式、还是独立设计。建议复用已有的 profile override 模式以保持代码风格一致。

---

## 5. 风险点

**[WARNING] CLI 二级命令实现复杂度可能被低估**

当前 `cli.py` 已经是 2153 行的巨型文件，使用纯 `argparse` 扁平子命令结构（约 40+ 个子命令）。新增 `api` 二级入口意味着引入嵌套子命令（`api` -> `snapshot` / `stock-list` 等 11 个原子命令），而 `argparse` 对嵌套子命令的支持不够优雅。

实现时有两种路径：
- **路径 A**：在 `build_parser()` 中为 `api` 添加二级 subparser -- 代码量会进一步膨胀。
- **路径 B**：在 `main()` 中对 `args.command` 做 `startswith("api:")` 匹配或单独解析。

方案未指定实现路径，建议在方案中明确选择，并考虑是否将 `api` 命令的实现抽到独立函数（如 `_handle_api_subcommand()`）以控制 `cli.py` 的膨胀速度。

**[WARNING] profile 配置文件路径的跨平台问题**

方案指定 `runtime/api-profiles.json` 作为配置路径。当前 `cli.py:87` 中 `PINGAN_LAST_ORDER_STATE_PATH = Path("runtime/pingan-last-order.json")` 使用相对路径，这意味着它依赖于 CWD（当前工作目录）。新配置文件如果也用相对路径，在不同 CWD 下行为不一致。

**建议**：基于项目根目录或 `__file__` 的父目录解析绝对路径，而非依赖 CWD。

**[INFO] 方案未定义错误处理策略**

`bridge.py` 的 `_run_tq_call` 已有统一错误封装（`ValueError` -> `INVALID_REQUEST`，其他异常 -> `EXECUTION_FAILED`）。方案未说明 `manager.py` 和 `domain` 层是否增加新的错误类型或错误码。建议 MVP 阶段沿用现有 `ErrorCode` 枚举（`models.py:8-15`），不做扩展。

---

## 6. 遗漏项

**[WARNING] 测试策略完全缺失**

方案没有提及任何测试计划。现有代码库中未发现测试文件。新增 4 个模块 + 1 个配置文件 + CLI 改动，至少应规划：

1. `manager.py` 的单元测试（mock bridge 层）
2. `market.py` / `meta.py` 的参数传递正确性测试
3. `runtime.py` 的 profile 合并逻辑测试
4. CLI `api` 入口的集成冒烟测试

**建议**：在开发顺序中插入测试任务，或在每个开发任务中内含测试要求。

**[WARNING] `__init__.py` 导出策略未定义**

方案目标结构（第 4 节）列出了新增的 `.py` 文件，但未说明 `tdxquant/api/__init__.py` 的变更策略。当前文件使用星号导出（`from .bridge import *`），新增模块后需要决定：

- 是否导出 `TdxApiManager`？
- 是否导出 `market` / `meta` 子模块？
- 还是保持 `__init__.py` 只导出 bridge 层？

**建议**：`__init__.py` 至少导出 `TdxApiManager`，使其可以直接 `from tdxquant.api import TdxApiManager` 使用。

**[INFO] 方案未提及日志策略**

`bridge.py` 当前没有使用 Python `logging` 模块。方案 5.2 节提到 `runtime.py` 负责"统一记录耗时"，但未说明使用什么日志基础设施（`print`、`logging`、还是写入结构化文件）。

**[INFO] `kline` 参数复杂度最高但方案未给出封装示例**

`run_tdx_data_kline`（`bridge.py:253-276`）有 8 个参数（`stock_list`, `period`, `start_time`, `end_time`, `count`, `dividend_type`, `field_list`, `fill_data`），是所有接口中最复杂的。方案 5.3 节只说 market 域"处理该领域的轻量参数整理"，但未给出 `kline` 这种多参数接口的具体封装策略。建议补充说明 profile 如何与这种复杂参数交互。

---

## 7. 开发顺序

**[GOOD]** 方案第 11 节的开发顺序基本合理。

`runtime.py` -> `market.py` -> `meta.py` -> `manager.py` -> `api-profiles.json` -> `cli.py` -> 验证，遵循了自底向上的依赖顺序。

**[WARNING] `manager.py` 应在 `market.py` / `meta.py` 之后但需注意依赖方向**

方案的开发顺序是 `runtime.py(1)` -> `market.py(2)` -> `meta.py(3)` -> `manager.py(4)`。这里有一个隐含问题：如果 `market.py` / `meta.py` 需要使用 `runtime.py` 提供的 profile 合并能力，那么它们是否应接受外部传入的已合并参数、还是自行调用 `runtime` 模块？

建议明确：domain 层（`market.py` / `meta.py`）不直接调用 `runtime.py` 的 profile 功能，而是由 `manager.py` 负责合并 profile 后将参数传给 domain 层。这样依赖方向更清晰：`runtime.py` <- `manager.py` -> `market.py` / `meta.py` -> `bridge.py`。

**[INFO] 建议在任务 1 和任务 2 之间插入一个"接口规范确认"检查点**

在 `runtime.py` 完成后、开始写 `market.py` 之前，建议先确认 domain 层调用 `bridge.py` 函数时的参数传递规范（是传 `kwargs`、还是用 dataclass 封装、还是纯位置参数）。这个决定会影响所有后续模块的实现风格。

---

## 8. 改进建议汇总

| # | 严重度 | 建议 | 说明 |
|---|--------|------|------|
| 1 | **CRITICAL** | 将 `tdxquant/api/runtime.py` 重命名为 `tdxquant/api/context.py` 或 `tdxquant/api/profile_helper.py` | 避免与已有的 `tdxquant/runtime.py`（被 `brokers/pingan.py:8` 引用）产生混淆 |
| 2 | **WARNING** | 补充 `send_user_block` 在 MVP 阶段的处置策略 | 该接口属于写操作且不在 `market`/`meta` 域中，需明确是暂时留在 bridge 直接调用还是临时归入某域 |
| 3 | **WARNING** | 补充测试策略或至少每个任务包含测试要求 | 4 个新模块 + CLI 改动没有任何测试计划，新增代码的回归风险无法控制 |
| 4 | **WARNING** | 明确 CLI `api` 二级命令的实现路径 | `cli.py` 已 2153 行，`argparse` 嵌套子命令会进一步膨胀，建议指定是否抽独立函数或引入子命令分发器 |
| 5 | **WARNING** | 补充 `api/__init__.py` 的变更说明 | 至少应导出 `TdxApiManager` 作为公共 API |
| 6 | **WARNING** | 明确 profile 配置文件使用绝对路径解析 | 避免与现有 `PINGAN_LAST_ORDER_STATE_PATH` 相同的 CWD 依赖问题 |
| 7 | **WARNING** | 重新考虑 `refresh_cache` 的归属 | 作为写操作放入只读 `meta` 域语义不清，建议直接作为 `manager` 方法 |
| 8 | **INFO** | 明确 domain 层不直接调用 profile 功能 | 依赖方向应为 `manager -> runtime + market/meta -> bridge`，避免 domain 层对 profile 模块的耦合 |
| 9 | **INFO** | 说明 `api-profiles.json` 与现有 `PINGAN_BUY_PROFILES` 模式的关系 | 复用已有模式可保持代码风格一致性 |
| 10 | **INFO** | 补充 `kline` 等复杂参数接口的封装策略说明 | 最复杂接口（8 个参数）的 profile 交互方式应给出示例 |

---

## 9. 引用文件索引

| 文件 | 相关性 |
|------|--------|
| `tdxquant/runtime.py:1-93` | 现有运行时路径解析模块，与方案新增文件名冲突 |
| `tdxquant/brokers/pingan.py:8` | 引用 `from ..runtime import resolve_runtime`，证明命名冲突有实际影响 |
| `tdxquant/api/bridge.py:131-170` | `_run_tq_call` 的短连接模式，MVP 阶段是否维持应明确 |
| `tdxquant/api/bridge.py:355-365` | `send_user_block` 未被方案纳入任何域 |
| `tdxquant/api/bridge.py:368-513` | 8 个 formula 相关函数的处置策略需显式说明 |
| `tdxquant/api/__init__.py:1-3` | 星号导出，新增模块后需变更 |
| `tdxquant/cli.py:88-137` | 现有 `PINGAN_BUY_PROFILES` 模式可作为新 profile 设计参考 |
| `tdxquant/cli.py:140-670` | `build_parser()` 约 530 行，嵌套子命令的膨胀风险 |
| `tdxquant/cli.py:87` | 相对路径依赖 CWD 的模式 |
| `tdxquant/DIRECTORY_PLAN.md:37-46` | 已有的拆分规划，与方案一致 |
| `tdxquant/models.py:8-15` | 现有 `ErrorCode` 枚举 |
