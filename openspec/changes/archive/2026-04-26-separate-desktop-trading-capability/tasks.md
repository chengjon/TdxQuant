## 1. Capability Planning

- [x] 1.1 梳理当前桌面自动化交易路径涉及的代码与命令边界，形成 capability 范围说明。
- [x] 1.2 定义 `tdx-desktop-trading-management` 的职责、非职责，以及它与 `tdx-api-management` 的并列关系。
- [x] 1.3 定义未来桌面交易顶层入口原则，明确不并入 `TdxApiManager`。

## 2. CLI Planning

- [x] 2.1 规划未来 `trade` 二级命令组的定位，明确它与 `api` 二级命令组的差异。
- [x] 2.2 定义现有扁平交易命令到未来 `trade` 组的兼容迁移原则。

## 3. Delivery Planning

- [x] 3.1 明确本次 change 只输出 capability 规划，不直接重构现有交易实现。
- [x] 3.2 列出后续建议的实现型 change，包括 `TradeManager`、`trade` CLI 收敛和 task 层编排三个方向。
