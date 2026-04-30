## 1. Sector Transaction API Tests

- [x] 1.1 为 `api sector-transaction-data`、`api sector-transaction-data-by-date` 以及对应 flat bridge 命令补 parser 和 dispatch 测试。
- [x] 1.2 为 `transaction` 域补板块交易数据 delegation 测试，并为 `TdxApiManager.transaction` 补显式字段透传、零值日期透传与 manager metadata 测试。

## 2. Sector Transaction API Implementation

- [x] 2.1 在 `bridge` 与 `transaction` 域中新增板块交易数据包装。
- [x] 2.2 在 `TdxApiManager.transaction` 与 CLI 中新增板块交易数据的 nested `api` 和 flat bridge 入口。

## 3. Verification And Docs

- [x] 3.1 更新 `docs/TdxQuant_Interface_Coverage_Matrix.md`，把 `bkjy` 从未覆盖迁移到已覆盖，并明确 `scjy` 仍待后续独立推进。
- [x] 3.2 运行定向测试、`compileall` 与 OpenSpec 校验，确认变更可进入归档阶段。
