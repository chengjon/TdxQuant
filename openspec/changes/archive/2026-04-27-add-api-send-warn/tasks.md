## 1. Send Warn API Tests

- [x] 1.1 为 `api send-warn` 和 `tdx-send-warn` 补 parser 与 dispatch 测试，确认批量列表参数可重复输入并透传。
- [x] 1.2 为 `runtime` 域补 `send_warn` delegation 测试，并为 `TdxApiManager.runtime` 补 manager metadata 与 `count` 透传测试。

## 2. Send Warn API Implementation

- [x] 2.1 在 `bridge` 与 `runtime` 域中新增 `send_warn` 包装。
- [x] 2.2 在 `TdxApiManager.runtime` 与 CLI 中新增 `send_warn` 的 nested `api` 和 flat bridge 入口。

## 3. Verification And Docs

- [x] 3.1 更新 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与 `docs/TdxQuant_API_System_Plan.md`，把 `send_warn` 从未覆盖迁移到已覆盖，并明确订阅治理仍待后续持久 session 包。
- [x] 3.2 运行定向测试、`compileall` 与 OpenSpec 校验，确认变更可进入归档阶段。
