## 1. Stock Transaction API Tests

- [x] 1.1 为 `api stock-transaction-data`、`api stock-transaction-data-by-date` 以及对应 flat bridge 命令补 parser 和 dispatch 测试。
- [x] 1.2 为 `transaction` 域补 delegation 测试，并为 `TdxApiManager.transaction` 补显式字段透传、零值日期透传与 manager metadata 测试。

## 2. Stock Transaction API Implementation

- [x] 2.1 在 `bridge` 中新增股票交易数据包装，并新增 `tdxquant/api/transaction.py` 域模块。
- [x] 2.2 在 `TdxApiManager` 中暴露 `transaction` 子域，并在 CLI 中新增 nested `api` 与 flat bridge 股票交易数据命令。

## 3. Verification And Docs

- [x] 3.1 更新 `docs/TdxQuant_Interface_Coverage_Matrix.md`，把 `gpjy` 从未覆盖迁移到已覆盖，并明确 `bkjy/scjy` 仍待后续独立推进。
- [x] 3.2 运行定向测试、`compileall` 与 OpenSpec 校验，确认变更可进入归档阶段。
