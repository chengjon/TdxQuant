## 1. Catalog Config

- [x] 1.1 增加统一 command catalog 配置文件与解析 helper。
- [x] 1.2 为 catalog entry 定义基础结构校验与 source/preset 解析。

## 2. CLI Entry

- [x] 2.1 增加顶层 `catalog` 命令组与列表入口。
- [x] 2.2 增加 `catalog run --entry ...` 执行入口，并复用既有 `task/report/trade` preset 分发逻辑。
- [x] 2.3 处理显式 CLI 参数覆盖 catalog 下游 preset 默认值。

## 3. Verification

- [x] 3.1 先补 catalog 解析、列表与分发测试。
- [x] 3.2 更新使用文档与示例配置。
- [x] 3.3 运行定向回归测试、语法校验和 OpenSpec 校验。
