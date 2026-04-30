## 1. Runtime Surface Tests

- [x] 1.1 为 `api trading-dates`、`api refresh-kline`、`api download-file` 补 parser 与 manager dispatch 测试。
- [x] 1.2 为 `runtime` 域补 domain delegation 与 manager metadata 测试。

## 2. Runtime Surface Implementation

- [x] 2.1 在 `bridge` 与新 `runtime` 域模块中新增 `get_trading_dates`、`refresh_kline`、`download_file` 包装。
- [x] 2.2 在 `TdxApiManager` 中新增 `runtime` 子域，并保留现有 `refresh_cache` 顶层治理动作。
- [x] 2.3 在 CLI 中新增 nested `api` 子命令与对应 flat bridge 命令并完成分发。

## 3. Verification

- [x] 3.1 更新能力覆盖矩阵和主方案文档中的 runtime 公共查询能力说明。
- [x] 3.2 运行定向测试、语法校验与 OpenSpec 校验。
