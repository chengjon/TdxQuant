## 1. Bundle Model

- [x] 1.1 扩展 bundle step 结构，支持稳定 step 名称与唯一性校验。
- [x] 1.2 增加 step 选择范围解析 helper。

## 2. Catalog CLI

- [x] 2.1 扩展 `catalog run --bundle ...` 支持 `--from-step` / `--to-step` / `--only-step`。
- [x] 2.2 执行结果补充选中范围与实际执行 step 元数据。
- [x] 2.3 扩展 `catalog list` 结果，返回 step 序号与名称。

## 3. Verification

- [x] 3.1 先补 step 解析、范围选择、局部执行与非法范围测试。
- [x] 3.2 更新示例 bundle 配置与使用文档。
- [x] 3.3 运行定向回归测试、语法校验和 OpenSpec 校验。
