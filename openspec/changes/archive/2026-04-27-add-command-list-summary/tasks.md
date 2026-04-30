## 1. List Summary Model

- [x] 1.1 为 catalog list 增加 summary view helper。
- [x] 1.2 为 entry / bundle 列表增加稳定排序。

## 2. CLI Integration

- [x] 2.1 扩展 `catalog list` 支持 `--view detailed|summary`。
- [x] 2.2 保持默认详细输出兼容，显式 summary 时裁剪最终输出。

## 3. Verification

- [x] 3.1 先补 parser、list ordering、handler summary 和 main 输出切换测试。
- [x] 3.2 更新使用文档。
- [x] 3.3 运行定向回归测试、语法校验和 OpenSpec 校验。
