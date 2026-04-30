## 1. Report CLI Group

- [x] 1.1 为 CLI 增加独立的 `report` 命令组。
- [x] 1.2 为 `report` 组增加 `ledger` / `daily` / `period` / `lookup` 子命令。
- [x] 1.3 提取共享分发逻辑，避免 `task` / `report` 双份报表分支。

## 2. Verification

- [x] 2.1 补充 CLI 解析测试覆盖 `report` 命令组。
- [x] 2.2 补充分发与 main 路由测试。
- [x] 2.3 更新使用文档并运行定向回归测试。
