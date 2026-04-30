## Why

查询主线已经补齐了官方文档中的财务、交易和 runtime 公共查询能力，但 `send_warn` 仍未进入标准 manager/CLI 入口。相比 `subscribe_hq` 这类需要持久运行时会话的能力，`send_warn` 是一次性写入调用，和当前 `bridge -> runtime -> manager -> CLI` 架构天然兼容，适合作为下一条独立小包推进。

## What Changes

- 在 `runtime` 子域中新增客户端预警发送能力，先收口：
  - `send_warn`
- 为 `TdxApiManager` 新增：
  - `manager.runtime.send_warn(...)`
- 为 nested `api` 命令新增：
  - `api send-warn`
- 为 flat bridge CLI 新增：
  - `tdx-send-warn`
- 保持 `stock_list`、`time_list` 和 `count` 等参数显式输入，不通过 profile 默认值隐式补齐批量预警内容。
- 在 CLI 中使用语义化 `--volume` 参数，并在 bridge 层映射到官方 `volum_list` 入参。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-management`: 扩展 `runtime` 子域，使其支持客户端预警发送。
- `tdx-api-cli-entry`: 扩展 nested `api` 与 flat bridge CLI，使其支持 `send_warn` 标准入口。

## Impact

- 影响 `tdxquant/api/bridge.py`、`tdxquant/api/runtime.py`、`tdxquant/api/manager.py` 和 `tdxquant/cli.py`。
- 影响 `tests/test_api_cli.py` 与 `tests/test_api_manager.py`。
- 影响 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与 `docs/TdxQuant_API_System_Plan.md`。
- 不处理 `subscribe_hq / unsubscribe_hq / get_subscribe_hq_stock_list` 的持久 runtime session 问题。
