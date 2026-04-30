## 1. Financial API Tests

- [x] 1.1 为 `api financial-data`、`api financial-data-by-date` 以及对应 flat bridge 命令补 parser 和 dispatch 测试。
- [x] 1.2 为 `financial` 域补 delegation 测试，并为 `TdxApiManager.financial` 补显式字段透传与 manager metadata 测试。

## 2. Financial API Implementation

- [x] 2.1 在 `bridge` 中新增专业财务数据包装，并新增 `tdxquant/api/financial.py` 域模块。
- [x] 2.2 在 `TdxApiManager` 中暴露 `financial` 子域，并在 CLI 中新增 nested `api` 与 flat bridge 专业财务命令。

## 3. Verification And Docs

- [x] 3.1 更新 `docs/TdxQuant_Interface_Coverage_Matrix.md`，必要时补记 `docs/TdxQuant_API_System_Plan.md` 的下一步说明。
- [x] 3.2 运行定向测试、`compileall` 与 OpenSpec 校验，确认变更可进入归档阶段。
