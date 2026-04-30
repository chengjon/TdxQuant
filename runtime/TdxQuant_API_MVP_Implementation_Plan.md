# TdxQuant API 顶层管理体系 MVP 实施方案

## 1. 目标

基于 [docs/TdxQuant_API_System_Plan.md](/opt/iflow/TdxQuant/docs/TdxQuant_API_System_Plan.md:1) 的总体方向，先为本项目落一版低风险、可持续扩展的 API 顶层管理体系。

本次只做查询类能力的顶层治理，不触碰现有平安桌面自动化交易链，不替换当前可用命令。

本阶段目标：

- 保留现有 `bridge.py` 和扁平 CLI 命令不变
- 增加统一 API 顶层入口 `TdxApiManager`
- 增加 `market` / `meta` 业务域
- 增加基础 profile 配置
- 增加二级 CLI 入口 `api`
- 为后续 `task` 层预留结构，但本阶段不强推落地

## 2. 当前项目现状

当前项目已经完成的基础：

- `tdxquant/api/bridge.py`
  - 已接入一批 TdxQuant 查询接口
  - 仍然承担底层桥接职责
- `tdxquant/desktop/`
  - 已承载桌面自动化交易链
- `tdxquant/cli.py`
  - 仍是统一 CLI 入口
  - 已存在稳定生产命令 `pingan-buy`
  - 已存在 profile 使用模式，可作为 API profile 设计参考

当前痛点：

- API 查询能力仍然集中在 `bridge.py`
- `cli.py` 命令持续扩张，参数组织会越来越重
- 日常调用缺少统一顶层入口
- 缺少 profile 驱动的 API 使用方式
- 缺少更贴近日常使用的组合入口

## 3. 本项目的边界约束

本项目必须遵守以下边界：

- 不重构现有桌面自动化交易路径
- 不废弃现有扁平 CLI 命令
- 不让 `manager` 直接承担底层桥接实现
- 不在本阶段引入交易执行类 API 顶层管理
- 不在本阶段大规模拆空 `bridge.py`

结论：

- `bridge.py` 保留，继续作为底层透传层
- 新层在它之上构建，而不是替换它

## 4. 目标结构

第一阶段完成后的目标目录如下：

```text
tdxquant/
  api/
    __init__.py
    bridge.py
    context.py
    manager.py
    market.py
    meta.py
  desktop/
    ...
  brokers/
    ...
runtime/
  api-profiles.json
```

后续阶段扩展：

```text
tdxquant/
  api/
    formula.py
    block.py
  tasks/
    __init__.py
    research.py
    watchlist.py
runtime/
  task-profiles.json
```

## 5. 模块职责设计

### 5.1 `tdxquant/api/bridge.py`

定位：底层桥接层。

职责：

- 一函数对应一底层 TdxQuant 接口
- 保留现有 `Result` 返回结构
- 处理运行时初始化、底层调用、序列化

禁止：

- 不做跨接口组合
- 不做复杂 profile 合并
- 不做业务场景任务

### 5.2 `tdxquant/api/context.py`

定位：API 顶层公共底座。

职责：

- 统一读取 API profile
- 统一合并默认参数和调用覆盖参数
- 统一记录耗时
- 统一生成调用上下文信息
- 统一封装 manager/domain 层所需公共逻辑

建议提供：

- `load_api_profiles()`
- `resolve_api_profile(profile_name, overrides)`
- `capture_api_timing(step_name, fn)`
- `build_manager_call_metadata(...)`
- `get_api_profile_path()`

说明：

- 不重复实现 `bridge.py` 的 `_init_tqcenter()`
- 本层是“顶层治理工具层”，不是新的底层连接实现层
- 使用绝对路径解析 `runtime/api-profiles.json`，不依赖当前工作目录
- 命名为 `context.py`，避免与现有 [tdxquant/runtime.py](/opt/iflow/TdxQuant/tdxquant/runtime.py:1) 混淆

### 5.3 `tdxquant/api/market.py`

定位：行情查询业务域。

本阶段纳入：

- `snapshot`
- `market_snapshot`
- `kline`
- `stock_info`
- `more_info`
- `cb_info`

职责：

- 按行情语义封装 `bridge.py`
- 处理该领域的轻量参数整理
- 接受 manager 已合并后的默认字段或开关

边界：

- `market.py` 不直接读取 profile 文件
- `market.py` 不直接调用 `context.py` 的 profile 合并逻辑
- `market.py` 只接收上层已经标准化后的参数

复杂参数说明：

- `kline` 是本阶段参数最多的接口
- profile 仅允许提供“默认值”，例如：
  - 默认 `field_list`
  - 默认 `fill_data`
  - 默认 `dividend_type`
- 显式调用参数优先级高于 profile 默认值
- `stock_list`、`period`、`start_time`、`end_time` 仍然必须由调用方明确传入，不通过 profile 隐式推导

### 5.4 `tdxquant/api/meta.py`

定位：元数据查询业务域。

本阶段纳入：

- `stock_list`
- `sector_list`
- `sector_stocks`
- `gb_info`
- `gp_one_data`

说明：

- `meta.py` 保持只读查询语义
- 不把运行时写动作塞入 `meta.py`

### 5.5 `tdxquant/api/manager.py`

定位：全局唯一顶层调用门面。

建议类名：

- `TdxApiManager`

职责：

- 聚合 `market` / `meta`
- 统一接收 `profile`
- 向下分发标准化参数
- 直接暴露运行时公共动作：
  - `refresh_cache()`
- 统一返回结果附加：
  - `api_profile`
  - `timing`
  - `manager`

建议形态：

```python
manager = TdxApiManager(profile="default")
manager.market.snapshot("688260.SH", fields=["Now"])
manager.meta.stock_list(market="16", list_type=1)
manager.refresh_cache(market="AG", force=False)
```

### 5.6 `runtime/api-profiles.json`

定位：API 参数预设层。

本阶段建议只做 3 到 5 个 profile：

- `default`
- `brief`
- `named_list`
- `research`
- `safe_read`

建议配置内容：

- `default_fields`
- `list_type`
- `auto_refresh_cache`
- `include_timing`
- `output_format`
- `timeout_hint`

实现约束：

- profile 合并模式复用现有 `pingan-buy` 的思路：
  - 先读预设
  - 再用显式传参覆盖
- 但配置载体使用 JSON 文件，而不是硬编码字典

### 5.7 `tdxquant/api/__init__.py`

定位：公共导出入口。

本阶段策略：

- 保留现有 bridge 兼容导出
- 新增导出 `TdxApiManager`

目标效果：

```python
from tdxquant.api import TdxApiManager
```

## 6. CLI 设计

### 6.1 原则

- 现有扁平命令全部保留
- 新增二级命令，不替代旧命令
- 先做 `api`，后做 `task`

### 6.2 第一阶段新增命令结构

```text
python -m tdxquant.cli api snapshot
python -m tdxquant.cli api market-snapshot
python -m tdxquant.cli api stock-info
python -m tdxquant.cli api more-info
python -m tdxquant.cli api cb-info
python -m tdxquant.cli api stock-list
python -m tdxquant.cli api sector-list
python -m tdxquant.cli api sector-stocks
python -m tdxquant.cli api gb-info
python -m tdxquant.cli api gp-one
python -m tdxquant.cli api refresh-cache
```

统一公共参数：

- `--profile`
- `--output`
- `--strategy-path`

### 6.3 CLI 与现有命令的关系

示例映射：

- 旧命令：`tdx-data-stock-list`
- 新命令：`api stock-list`

二者都调用同一底层 manager/domain 能力。

这样可以保证：

- 旧脚本继续可用
- 新入口更适合日常使用
- 后续文档逐步切换到新入口

### 6.4 CLI 实现路径

为控制 [tdxquant/cli.py](/opt/iflow/TdxQuant/tdxquant/cli.py:1) 继续膨胀，本阶段采用以下策略：

- 仍使用 `argparse`
- 为 `api` 增加二级 subparser
- 但把解析后的执行逻辑抽到独立函数，例如：
  - `_build_api_parser(...)`
  - `_handle_api_subcommand(args)`

这样可以避免把所有 `api` 二级命令逻辑继续堆在 `main()` 的长分支中。

## 7. 数据流设计

标准调用链建议如下：

```text
CLI / Python 调用
  -> TdxApiManager
    -> market/meta domain
      -> bridge.py
        -> tqcenter
```

职责边界：

- CLI：收参数，做入口分发
- Manager：合并 profile、记录 timing、统一结果、执行少量运行时公共动作
- Domain：按业务域调用底层 API，不直接处理 profile 文件
- Bridge：底层透传

## 8. MVP 阶段特殊处置策略

以下接口在 MVP 阶段显式按特殊策略处理：

- `send_user_block`
  - 属于写操作
  - 本阶段不纳入 `manager`
  - 保留在 `bridge.py` + 旧 CLI 命令中直接使用
  - 等 `block.py` 阶段再纳入新体系

- formula 系列接口
  - 本阶段不纳入 `api` 二级入口
  - 保留旧扁平命令继续使用
  - 等 `formula.py` 阶段统一纳入

- `_run_tq_call` 的短连接模式
  - MVP 阶段维持现状
  - 即每次调用仍是“初始化 -> 执行 -> 关闭”
  - 本阶段不实现 `tqcenter` 长连接复用
  - `manager` 中所谓“统一管理”仅指 profile、timing、结果治理，不改变底层连接模型

## 9. 第一阶段详细开发任务

### 任务 1：新增 `context.py`

输出文件：

- `tdxquant/api/context.py`

实现内容：

- profile 加载
- profile 合并
- 调用计时工具
- manager 附加信息构造

测试要求：

- profile 读取测试
- profile 覆盖合并测试
- 配置路径绝对路径解析测试

### 任务 2：接口规范确认检查点

在开始 `market.py` / `meta.py` 之前，先确认统一约定：

- domain 层统一使用关键字参数调用 `bridge.py`
- domain 层不直接读取 profile 文件
- manager 负责把 profile 合并为显式参数后再传入 domain

### 任务 3：新增 `market.py`

输出文件：

- `tdxquant/api/market.py`

实现内容：

- `snapshot`
- `market_snapshot`
- `kline`
- `stock_info`
- `more_info`
- `cb_info`

测试要求：

- 各方法参数向 `bridge.py` 透传的正确性测试
- `kline` 默认值与显式覆盖优先级测试

### 任务 4：新增 `meta.py`

输出文件：

- `tdxquant/api/meta.py`

实现内容：

- `stock_list`
- `sector_list`
- `sector_stocks`
- `gb_info`
- `gp_one_data`

测试要求：

- `stock_list` / `sector_list` / `sector_stocks` 的 `list_type` 透传测试
- `gp_one_data` 参数透传测试

### 任务 5：新增 `manager.py`

输出文件：

- `tdxquant/api/manager.py`

实现内容：

- `TdxApiManager`
- `market` / `meta` 聚合
- profile 注入
- timing 注入
- `refresh_cache` 直接方法

测试要求：

- `manager.market` / `manager.meta` 的无状态代理访问测试
- `refresh_cache` 调度测试
- 结果附加 `api_profile` / `timing` 测试

### 任务 6：新增 profile 配置

输出文件：

- `runtime/api-profiles.json`

初始配置：

- `default`
- `brief`
- `named_list`
- `research`

### 任务 7：更新 `api/__init__.py`

修改文件：

- `tdxquant/api/__init__.py`

实现内容：

- 保留 bridge 兼容导出
- 新增 `TdxApiManager` 导出

### 任务 8：为 CLI 新增 `api` 二级入口

修改文件：

- `tdxquant/cli.py`

实现内容：

- 添加 `api` 顶层子命令
- 添加其下的原子命令
- 通过 `TdxApiManager` 调用
- 将执行逻辑抽到独立处理函数

测试要求：

- `api` 帮助命令冒烟测试
- 至少 2 个 `api` 二级命令的参数解析冒烟测试

## 10. 第一阶段不做的内容

避免范围膨胀，本阶段明确不做：

- 不拆 `formula.py`
- 不拆 `block.py`
- 不新增 `task` 二级命令
- 不把桌面自动化路径并入 manager
- 不改现有 `pingan-buy` 相关逻辑
- 不引入交易执行类 API 顶层治理
- 不把 `send_user_block` 纳入新 manager 体系
- 不把 formula 系列命令迁入 `api` 二级入口
- 不实现 `tqcenter` 长连接复用
- 不扩展新的错误码，沿用现有 [models.py](/opt/iflow/TdxQuant/tdxquant/models.py:1) 中的 `ErrorCode`

## 11. 验收标准

第一阶段完成后，应满足：

- 现有扁平 CLI 命令继续可用
- 新增 `api` 二级命令可用
- 查询类能力可以通过 `TdxApiManager` 调用
- profile 可以影响默认行为
- 结果中可统一看到 `timing` 和 `api_profile`
- 代码结构形成 `bridge -> domain -> manager` 的稳定分层
- `send_user_block` 与 formula 系列旧入口不受影响
- 配置文件路径不依赖当前工作目录
- 至少具备基础单元测试 / 冒烟测试覆盖

## 12. 推荐开发顺序

建议严格按下面顺序开发：

1. `context.py`
2. 接口规范确认检查点
3. `market.py`
4. `meta.py`
5. `manager.py`
6. `api-profiles.json`
7. `api/__init__.py`
8. `cli.py` 新增 `api` 二级入口
9. 单元测试与 CLI 冒烟测试
10. 基础验证与帮助命令检查

## 13. 本阶段输出结论

本项目适合采用以下方案：

- 底层不动：保留 `bridge.py`
- 先做查询：不碰交易自动化生产链
- 中间分层：新增 `market` / `meta`
- 顶层统一：新增 `TdxApiManager`
- 顶层公共底座：新增 `context.py`
- 参数减负：新增 API profile，并复用现有 profile override 风格
- 命令演进：新增 `api` 二级 CLI，而不是废弃旧命令

这是一条对当前项目风险最低、但对后续长期维护收益最高的路线。
