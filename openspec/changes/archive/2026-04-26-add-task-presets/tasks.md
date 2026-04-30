## 1. Task Preset Config

- [x] 1.1 增加 runtime task preset 配置文件与解析 helper。
- [x] 1.2 为 task preset 定义增加基本结构校验与默认 command/profile 解析。

## 2. CLI Entry

- [x] 2.1 为 `task` 命令组增加 preset 列表入口。
- [x] 2.2 为 `task` 命令组增加 preset 执行入口，并复用既有稳定 task workflow 分发逻辑。
- [x] 2.3 处理显式 CLI 参数覆盖 preset 默认值与最终兜底默认值。

## 3. Verification

- [x] 3.1 先补 task preset 解析、列表与分发测试。
- [x] 3.2 更新 task 使用文档与示例配置。
- [x] 3.3 运行定向回归测试、语法校验和 OpenSpec 校验。
