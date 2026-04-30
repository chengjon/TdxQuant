# TdxQuant API MVP 兼容性与范围说明

## 已纳入新 API 管理体系

本次 MVP 已纳入 `TdxApiManager` 和 `api` 二级 CLI 的查询类能力：

- `snapshot`
- `market_snapshot`
- `stock_info`
- `more_info`
- `cb_info`
- `kline`
- `stock_list`
- `sector_list`
- `sector_stocks`
- `gb_info`
- `gp_one_data`
- `refresh_cache`

对应代码入口：

- `tdxquant/api/context.py`
- `tdxquant/api/market.py`
- `tdxquant/api/meta.py`
- `tdxquant/api/manager.py`

对应 CLI 入口：

- `python -m tdxquant.cli api ...`

## 仍保留在旧入口的能力

以下能力本次没有纳入 `TdxApiManager`，继续保留原有 bridge/CLI 路径：

- `send_user_block`
- formula 系列命令：
  - `tdx-formula-format-data`
  - `tdx-formula-set-data`
  - `tdx-formula-set-data-info`
  - `tdx-formula-get-data`
  - `tdx-formula-zb`
  - `tdx-formula-xg`
  - `tdx-formula-exp`
  - `tdx-formula-mul-xg`
  - `tdx-formula-mul-zb`

保留原因：

- `send_user_block` 属于写操作，应在后续 `block.py` 阶段再纳入新体系
- formula 系列应在后续 `formula.py` 阶段统一纳入，避免 MVP 范围膨胀

## 保持不变的兼容性结论

- 现有扁平 CLI 命令继续可用
- 现有桌面自动化交易链不受本次 API 管理体系改造影响
- `bridge.py` 仍保留为底层透传层
- `_run_tq_call` 仍维持“初始化 -> 执行 -> 关闭”的短连接模式

## MVP 边界

本次只解决：

- 查询类能力的顶层组织
- profile 驱动的日常使用方式
- 新旧 CLI 共存

本次不解决：

- 交易执行类 API 顶层治理
- 自选股/板块写操作统一纳管
- formula 域统一管理
- `task` 场景层
- `tqcenter` 长连接复用
