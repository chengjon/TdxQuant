# 2026-04-25 PingAn Buy Fast Stable v2

## 1. 用途

这份快照用于固化当前已实机验证通过、且截至目前速度最快的稳定版本。

这版不是简单沿用 v1，而是在 v1 基础上继续验证出一个新的有效组合：

- `price/quantity` 使用 `hybrid_win32`
- `confirm_lookup/result_dialog_lookup` 使用 `win32_experimental`

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
- `dialog_lookup_mode=win32_experimental`
- Win32 顶层窗口枚举定位：
  - `买入交易确认`
  - `提示`

## 4. 本版推荐命令

```powershell
python -m tdxquant.cli --exe-path "D:\ProgramData\PinganSec\TdxW.exe" --title-key "平安证券" pingan-buy --port COM3 --profile turbo --code 516820 --price 0.35 --quantity 100 --output pingan-submit-once-result.json
```

等价的显式展开参数是：

- `--price-quantity-input-mode hybrid_win32`
- `--dialog-lookup-mode win32_experimental`

如果希望进一步缩短输入，也可以直接使用脚本：

```powershell
.\scripts\pingan-buy-turbo.ps1 -Code 516820 -Price 0.35 -Quantity 100
```

如果需要批量连单，可以直接使用批量脚本：

```powershell
.\scripts\pingan-buy-turbo-batch.ps1 -InputPath .\runtime\orders.json
```

仓库里也提供了可直接复制修改的模板：

- `runtime/orders.sample.json`
- `runtime/orders.sample.csv`

JSON 队列示例：

```json
[
  { "id": "001", "code": "516820", "price": "0.35", "quantity": 100 },
  { "id": "002", "code": "159869", "price": "0.42", "quantity": 100 }
]
```

CSV 队列示例：

```csv
id,code,price,quantity
001,516820,0.35,100
002,159869,0.42,100
```

## 5. 本版稳定实测基线

本次固化采用的成功结果：

- 总耗时：约 `12.41s`
- 合同号：`0361808002`
- `result_dialog.lookup_mode`：`win32_experimental`

关键耗时项：

- `set_code`：约 `3504ms`
- `set_price`：约 `3430ms`
- `set_quantity`：约 `3363ms`
- `focus_quantity_input`：约 `63ms`
- `confirm_lookup`：约 `8ms`
- `result_dialog_lookup`：约 `205ms`

## 6. 相比 v1 的变化

v1 的稳定基线约为 `23.75s`，而 v2 约为 `12.41s`。

主要差异不是输入阶段，而是弹窗阶段：

- `confirm_lookup`：从秒级下降到毫秒级
- `result_dialog_lookup`：从秒级下降到毫秒级

## 7. 风险边界

虽然这版已经实机成功，但它相比 v1 多引入了一条新的实验式查找策略，因此要明确记录边界：

- 默认生产配置仍然不应自动切换到这组参数
- 只有在当前客户端版本、当前窗口结构稳定时，这组参数才应视为推荐方案
- 如果后续客户端升级导致顶层窗口标题或结构变化，应优先回退到 v1

## 8. 快照文件

代码副本位于：

- `code/tdxquant/cli.py`
- `code/tdxquant/uia_inspector.py`
- `code/tdxquant/win32_api.py`
- `code/tests/test_runtime.py`
- `code/scripts/pingan-buy-turbo.ps1`
- `code/scripts/pingan-buy-turbo-batch.ps1`

## 9. 回退建议

如果后续出现下面任一问题：

- 实验版弹窗定位失效
- 卡在买入确认或结果窗
- 合同号提取失败
- 实测速度不再优于 v1

优先回退到：

- v2 失败但需要保留实验输入优化时：回退到 `stable-v1`
- 需要继续调查 Win32 弹窗策略时：以本快照为实验起点，不要直接修改 v1 快照
