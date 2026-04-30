## 1. Context and Profile Foundation

- [x] 1.1 新增 `tdxquant/api/context.py`，实现 API profile 绝对路径解析、配置读取、`profile + override` 合并和 timing 工具。
- [x] 1.2 新增 `runtime/api-profiles.json`，提供 MVP 所需的 `default`、`brief`、`named_list`、`research`、`safe_read` 预设。
- [x] 1.3 为 `context.py` 增加基础测试，覆盖配置路径解析、profile 读取和显式覆盖优先级。

## 2. Domain Layer

- [x] 2.1 新增 `tdxquant/api/market.py`，封装 `snapshot`、`market_snapshot`、`kline`、`stock_info`、`more_info`、`cb_info`，并保持无状态与 profile 无关。
- [x] 2.2 新增 `tdxquant/api/meta.py`，封装 `stock_list`、`sector_list`、`sector_stocks`、`gb_info`、`gp_one_data`，并保持无状态与 profile 无关。
- [x] 2.3 为 `market.py` 和 `meta.py` 增加参数透传测试，重点覆盖 `kline` 默认值覆盖规则和 `list_type` 透传行为。

## 3. Manager Entry Point

- [x] 3.1 新增 `tdxquant/api/manager.py`，实现 `TdxApiManager`、无状态 `market` / `meta` 访问代理，以及 manager 级 `refresh_cache()` 方法。
- [x] 3.2 更新 `tdxquant/api/__init__.py`，在保留现有 bridge 兼容导出的同时导出 `TdxApiManager`。
- [x] 3.3 为 `manager.py` 增加测试，覆盖 manager 元数据附加、`refresh_cache()` 调度和 `from tdxquant.api import TdxApiManager` 的公共导出可用性。

## 4. CLI Integration

- [x] 4.1 在 `tdxquant/cli.py` 中新增 `api` 二级命令组，并将构建与执行逻辑抽到独立辅助函数中。
- [x] 4.2 将 MVP 范围内的查询命令接入 `TdxApiManager`，统一支持 `--profile`、`--output`、`--strategy-path`。
- [x] 4.3 明确保留现有扁平命令、`send_user_block` 和 formula 系列旧入口不变，并为 `api` 二级命令补充 CLI 冒烟测试。

## 5. Verification

- [x] 5.1 运行基础验证，确认 `python -m compileall tdxquant` 通过且新增模块可正常导入。
- [x] 5.2 验证 `python -m tdxquant.cli api -h` 及至少两个 `api` 子命令帮助输出正确。
- [x] 5.3 记录本次 MVP 范围、保留旧入口的兼容性结论，以及未纳入 `manager` 的 capability 边界。
