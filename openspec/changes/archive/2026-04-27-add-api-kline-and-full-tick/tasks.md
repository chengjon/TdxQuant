## 1. Query Surface Tests

- [x] 1.1 为 `api kline` 与 `api full-tick` 补 parser 测试。
- [x] 1.2 为 `market.full_tick(...)` 和新 CLI 分发补 manager / dispatch 测试。

## 2. Query Surface Implementation

- [x] 2.1 在 `bridge`、`market`、`manager` 中新增显式 `full_tick` 入口，并保持 `snapshot` 兼容。
- [x] 2.2 在 `api` 二级命令中新增 `kline` 与 `full-tick` 子命令并完成分发。

## 3. Verification

- [x] 3.1 更新能力覆盖矩阵或相关使用文档中的入口说明。
- [x] 3.2 运行定向测试、语法校验与 OpenSpec 校验。
