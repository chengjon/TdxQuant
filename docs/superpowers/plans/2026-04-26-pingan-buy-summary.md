# PingAn Buy Automation Summary

更新日期：`2026-04-26`

## 1. 目标与结果

本轮工作的目标，是把平安证券自动买入链路从“可用但偏慢、参数偏长、回溯不方便”收口到一个可长期复用的稳定方案。

当前已经完成：

- 自动下单
- 自动推进买入确认
- 自动关闭结果窗
- 命令执行后主界面恢复，可继续下一单
- 合同号自动提取
- 合同号回填到结果 JSON、`runtime/pingan-last-order.json`、日志
- 高层命令参数化
- 稳定版本快照归档
- 单单脚本入口
- 批量连单脚本入口

## 2. 性能演进

本轮关键性能节点如下：

- 探测型高层命令：约 `70.15s`
- 第一版快路径：约 `30.94s`
- 窗口缓存版：约 `28.93s`
- UIA 定点查找 + 缓存版：约 `27.83s`
- `hybrid_win32` 稳定基线：约 `23.75s`
- `hybrid_win32 + win32_experimental`：约 `12.41s`
- `turbo` profile 复测：约 `12.92s`

结论：

- 真正有效的性能突破来自两个方向
- 输入阶段：`price/quantity` 使用 `hybrid_win32`
- 弹窗阶段：`confirm_lookup/result_dialog_lookup` 使用 `win32_experimental`

## 3. 当前推荐方案

当前最快且已实机验证通过的推荐方案是：

- `pingan-buy --profile turbo`

它内置：

- `price_quantity_input_mode=hybrid_win32`
- `dialog_lookup_mode=win32_experimental`

推荐命令：

```powershell
python -m tdxquant.cli --exe-path "D:\ProgramData\PinganSec\TdxW.exe" --title-key "平安证券" pingan-buy --port COM3 --profile turbo --code 516820 --price 0.35 --quantity 100 --output pingan-submit-once-result.json
```

## 4. 当前最短入口

单单脚本：

```powershell
.\scripts\pingan-buy-turbo.ps1 -Code 516820 -Price 0.35 -Quantity 100
```

批量脚本：

```powershell
.\scripts\pingan-buy-turbo-batch.ps1 -InputPath .\runtime\orders.json
```

模板文件：

- `runtime/orders.sample.json`
- `runtime/orders.sample.csv`

## 5. 稳定版本归档

当前已经归档两版稳定快照：

### stable-v1

- 路径：`docs/stable-snapshots/2026-04-25-pingan-buy-fast-stable-v1/`
- 特征：
  - 保留 `hybrid_win32`
  - 保留缓存聚焦优化
  - 不使用 Win32 实验版弹窗定位
- 典型耗时：约 `23.75s`

### stable-v2

- 路径：`docs/stable-snapshots/2026-04-25-pingan-buy-fast-stable-v2/`
- 特征：
  - 保留 `hybrid_win32`
  - 保留缓存聚焦优化
  - 使用 `win32_experimental` 弹窗定位
  - 含单单脚本与批量脚本快照
- 典型耗时：约 `12.41s`

稳定快照总索引：

- `docs/stable-snapshots/README.md`

## 6. 关键脚本与文件

核心命令入口：

- `tdxquant/cli.py`
- `tdxquant/uia_inspector.py`
- `tdxquant/win32_api.py`

脚本入口：

- `scripts/pingan-buy-turbo.ps1`
- `scripts/pingan-buy-turbo-batch.ps1`

状态与结果：

- `runtime/pingan-last-order.json`
- `pingan-submit-once-result.json`

## 7. 风险边界

当前推荐方案虽然已经实机验证，但仍应明确边界：

- `win32_experimental` 依赖当前客户端的顶层弹窗标题和结构
- 如果客户端升级、窗口标题变化、弹窗结构变化，速度优势可能失效
- 一旦发现卡在确认窗或结果窗，应优先回退到 `stable-v1`

## 8. 建议使用顺序

建议以后按下面顺序使用：

1. 日常单单：直接用 `.\scripts\pingan-buy-turbo.ps1`
2. 批量连单：用 `.\scripts\pingan-buy-turbo-batch.ps1`
3. 如果出现异常：
   - 先看 `pingan-submit-once-result.json`
   - 再看 `runtime/pingan-last-order.json`
4. 如果实验版弹窗定位不稳定：
   - 回退到 `stable-v1`
5. 如果后续再做优化：
   - 以 `stable-v2` 为实验起点

## 9. 当前最终结论

截至 `2026-04-26`，这套平安证券自动买入链路已经从“功能打通”推进到“具备固定流程、参数化入口、稳定版本快照、单单脚本、批量脚本、可回退基线”的状态。

如果后续没有新的客户端结构变化，当前最实用的方案就是：

- `--profile turbo`
- 单单用 `pingan-buy-turbo.ps1`
- 批量用 `pingan-buy-turbo-batch.ps1`
