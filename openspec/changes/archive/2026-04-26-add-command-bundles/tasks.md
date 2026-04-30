## 1. Bundle Config

- [x] 1.1 增加 command bundle 配置文件与解析 helper。
- [x] 1.2 增加 bundle step 结构校验与 entry 引用解析。

## 2. Catalog CLI

- [x] 2.1 扩展 `catalog list` 支持 bundle 列表与详情查看。
- [x] 2.2 扩展 `catalog run` 支持执行 bundle，并复用既有 entry 分发逻辑。
- [x] 2.3 处理 step 默认参数与显式 CLI 参数覆盖关系，以及 top-level 输出聚合。

## 3. Verification

- [x] 3.1 先补 bundle 解析、列表、分发与失败短路测试。
- [x] 3.2 更新 runtime 配置与使用文档。
- [x] 3.3 运行定向回归测试、语法校验和 OpenSpec 校验。
