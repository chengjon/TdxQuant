## 1. Summary Model

- [x] 1.1 为 catalog entry / bundle 的 run 和 plan 结果增加 summary view helper。
- [x] 1.2 定义最终序列化时的 summary 输出切换。

## 2. CLI Integration

- [x] 2.1 扩展 `catalog run` / `catalog plan` 支持 `--view detailed|summary`。
- [x] 2.2 保持默认详细输出兼容，显式 summary 时裁剪最终输出。

## 3. Verification

- [x] 3.1 先补 parser、handler summary 和 main 输出切换测试。
- [x] 3.2 更新使用文档。
- [x] 3.3 运行定向回归测试、语法校验和 OpenSpec 校验。
