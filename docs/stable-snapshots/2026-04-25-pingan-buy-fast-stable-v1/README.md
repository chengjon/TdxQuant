# 2026-04-25 PingAn Buy Fast Stable v1

## 1. 用途

这份快照用于固化当前已经实机验证通过的稳定版本，避免后续继续做性能实验时丢失可回退基线。

本快照包含两部分：

- 代码原件副本
- 稳定版本说明文档

## 2. 当前稳定版本定义

本稳定版本对应的能力边界如下：

- `pingan-buy` 可完成自动下单
- 可自动推进买入确认
- 可自动关闭结果窗
- 主界面在命令结束后恢复，可继续下一单
- 合同号可稳定提取并回填到结果 JSON、`runtime/pingan-last-order.json` 与日志

## 3. 本版保留的有效优化

- `pingan-buy` 高层命令封装
- `stable|balanced|fast` profile
- `timing.total_ms` 与 `timing.steps`
- `price/quantity` 的 `hybrid_win32`
- `focus_quantity_input` 的缓存控件复用

## 4. 本版明确撤回的实验

- 确认框/结果窗的 UIA 顶层直查实验

撤回原因：

- 实机看不到稳定收益
- 出现过确认窗无法识别导致流程停在“买入确认”的问题
- 即使成功，耗时也比稳定基线更高

## 5. 当前稳定实测基线

本次固化时采用的稳定结果：

- 命令：`pingan-buy --profile balanced --price-quantity-input-mode hybrid_win32`
- 总耗时：约 `23.75s`
- 合同号：`0363211004`

关键耗时项：

- `set_code`：约 `3462ms`
- `set_price`：约 `3401ms`
- `set_quantity`：约 `3296ms`
- `focus_quantity_input`：约 `62ms`
- `confirm_lookup`：约 `4771ms`
- `result_dialog_lookup`：约 `3301ms`

## 6. 快照文件

代码副本位于：

- `code/tdxquant/cli.py`
- `code/tdxquant/uia_inspector.py`
- `code/tests/test_runtime.py`

## 7. 后续版本保存规则

以后每次出现新的稳定版本，都按同样结构新增一个目录：

- `docs/stable-snapshots/<日期>-<主题>-stable-vN/`

目录内至少包含：

- `README.md`
- `code/tdxquant/cli.py`
- `code/tdxquant/uia_inspector.py`
- `code/tests/test_runtime.py`

如果某次稳定版本还依赖其他关键文件，也一并复制进去。

## 8. 回退使用建议

如果后续实验导致：

- 确认框无法自动推进
- 结果窗无法自动关闭
- 合同号提取失效
- 总耗时明显回升

优先用本目录中的代码副本覆盖当前工作代码，再重新实机验证。
