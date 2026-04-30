# TdxQuant 目录规划

## 目标

在不打断现有命令与交易流程的前提下，把项目拆成两条主线：

- `tdxquant/api/`
  - 对接 `tqcenter` 的运行时 API 桥接层。
  - 负责行情、板块、公式、自选股等 TdxQuant 文档能力封装。
- `tdxquant/desktop/`
  - 承载桌面自动化链路。
  - 包括 UIA、Win32、HID、窗口探测等能力。
- `tdxquant/brokers/`
  - 券商适配层。
  - 当前重点是平安证券买入页控件识别与提交流程。
- `tdxquant/trade/`
  - 桌面交易顶层管理层。
  - 负责 profile、状态回填、事件日志、顶层交易门面。

## 当前落地方式

本次先采用“新目录承载 + 旧入口兼容”的低风险方式：

- 新的实际实现入口：
  - `tdxquant/api/bridge.py`
  - `tdxquant/desktop/uia.py`
  - `tdxquant/desktop/win32.py`
  - `tdxquant/desktop/hid.py`
  - `tdxquant/desktop/inspect.py`
- 保留旧兼容文件：
  - `tdxquant/tdx_api_bridge.py`
  - `tdxquant/uia_inspector.py`
  - `tdxquant/win32_api.py`
  - `tdxquant/hid_bridge.py`
  - `tdxquant/inspector.py`

这些旧文件现在只做转发，避免已有脚本、历史命令、稳定版快照说明失效。

## 后续目录规则

后续实现 `docs/TdxQuant接口说明文档.md` 中的新功能时，统一按下面规则落目录：

- 行情与基础数据能力：优先进入 `tdxquant/api/bridge.py`
- 若 API 数量继续增长，再拆分为：
  - `tdxquant/api/market.py`
  - `tdxquant/api/meta.py`
  - `tdxquant/api/formula.py`
  - `tdxquant/api/block.py`
- 桌面自动化实验能力：优先进入 `tdxquant/desktop/`
- 券商特有识别逻辑：进入 `tdxquant/brokers/`
- 顶层桌面交易治理：进入 `tdxquant/trade/`
- CLI 统一在 `tdxquant/cli.py` 暴露

## 本次已先纳入的新接口

已接入到 `tdxquant/api/bridge.py`：

- `get_market_snapshot`
- `get_more_info`
- `get_cb_info`
- `get_gb_info`
- `refresh_cache`
- `send_user_block`

对应 CLI 命令：

- `tdx-data-market-snapshot`
- `tdx-data-more-info`
- `tdx-data-cb-info`
- `tdx-data-gb-info`
- `tdx-refresh-cache`
- `tdx-send-user-block`
