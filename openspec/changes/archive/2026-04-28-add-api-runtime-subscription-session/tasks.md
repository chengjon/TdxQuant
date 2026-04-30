## 1. Subscription Session Tests

- [x] 1.1 为持久 runtime subscription session 补生命周期测试，覆盖初始化一次、多次调用复用、显式关闭与 use-after-close 错误。
- [x] 1.2 为 `manager.runtime.open_subscription_session(...)` 补 manager 级测试，覆盖 session 打开、`subscribe_hq / unsubscribe_hq / get_subscribe_hq_stock_list` 代理，以及 metadata / timing / session_id 附加。

## 2. Subscription Session Implementation

- [x] 2.1 在 `tdxquant/api/bridge.py` 中新增持久订阅 session 抽象，提供 `subscribe_hq(...)`、`unsubscribe_hq(...)`、`get_subscribe_hq_stock_list()`、`close()` 与上下文管理能力。
- [x] 2.2 在 `tdxquant/api/runtime.py` 与 `tdxquant/api/manager.py` 中新增 session 打开入口和 manager-aware session 包装，并保持现有 one-shot runtime 能力不受影响。

## 3. Docs And Verification

- [x] 3.1 更新 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与 `docs/TdxQuant_API_System_Plan.md`，把订阅治理从“未覆盖”推进为“已有持久 session 管理层能力，CLI/任务层待后续扩展”。
- [x] 3.2 运行定向测试、必要的全量测试、`compileall` 与 OpenSpec 校验，确认 change 进入 apply-ready / implementation-ready 状态。
