## Why

查询主线已经补齐了大部分一次性数据查询与 runtime 动作，但 `subscribe_hq / unsubscribe_hq / get_subscribe_hq_stock_list` 仍未进入标准 API 管理层。官方文档明确要求订阅回调依赖持续运行的策略进程，而当前 `bridge -> runtime -> manager -> CLI` 的 one-shot 调用模型会在每次调用后关闭 `tqcenter`，因此不能再按已有同步 wrapper 方式硬接。

## What Changes

- 新增一层持久 runtime 订阅 session 能力，用于维持 `tqcenter` 初始化状态与订阅生命周期。
- 在 `runtime` 子域中新增 manager 级 session 打开入口，用于在单个 Python 进程内复用订阅会话。
- 在持久 session 内标准化收口官方三项订阅治理能力：
  - `subscribe_hq`
  - `unsubscribe_hq`
  - `get_subscribe_hq_stock_list`
- 明确把 CLI 的直接 one-shot 订阅入口排除在本次范围外，避免产出语义错误的伪订阅命令。
- 为后续 task 层或守护进程式订阅入口预留可复用的 session 基础设施。

## Capabilities

### New Capabilities

- `tdx-runtime-subscription-session`: 定义 TongDaXin runtime 持久订阅 session 的生命周期、订阅治理接口与关闭语义。

### Modified Capabilities

- `tdx-api-management`: 扩展 `runtime` 子域，使其支持打开和使用持久订阅 session，而不是把订阅接口塞入现有 one-shot manager 调用模型。

## Impact

- 影响 `tdxquant/api/bridge.py`、`tdxquant/api/runtime.py` 与 `tdxquant/api/manager.py`。
- 影响 `tests/test_api_manager.py`，并可能新增面向 session 生命周期的测试。
- 影响 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与 `docs/TdxQuant_API_System_Plan.md`。
- 本次不影响 `tdxquant/cli.py` 的标准 one-shot API 命令面，也不处理 task 层长期运行入口。
