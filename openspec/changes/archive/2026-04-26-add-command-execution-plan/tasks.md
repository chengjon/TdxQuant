## 1. Catalog Plan Model

- [x] 1.1 增加 entry / bundle planning helper。
- [x] 1.2 统一整理可序列化的 resolved args 输出。

## 2. CLI Entry

- [x] 2.1 扩展 `catalog` 命令组，新增 `plan` 子命令。
- [x] 2.2 支持 `catalog plan --entry ...`。
- [x] 2.3 支持 `catalog plan --bundle ...` 及 step 范围选择。

## 3. Verification

- [x] 3.1 先补 parser、entry plan、bundle plan 和无副作用测试。
- [x] 3.2 更新使用文档。
- [x] 3.3 运行定向回归测试、语法校验和 OpenSpec 校验。
