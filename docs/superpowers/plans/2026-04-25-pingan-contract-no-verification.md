# PingAn 合同号自动提取验收清单

本文用于在 Windows 实机上验收 `pingan-buy-submit-once` 的合同号自动提取与回填。

## 1. 验收目标

一次成功下单后，需要同时满足下面 5 项：

- 结果提示窗正常出现
- 结果提示窗能自动关闭
- 主界面恢复到可继续下一单的状态
- 命令输出 JSON 中存在 `data.result_dialog.contract_no`
- `runtime/pingan-last-order.json` 与命令 stderr 日志中都能看到同一个合同号

## 2. 执行命令

按你的实际环境替换参数后执行：

```bash
python -m tdxquant.cli --exe-path D:\ProgramData\PinganSec\TdxW.exe --title-key "平安证券" pingan-buy-submit-once --port COM3 --hid-pre-delay 3 --code 516820 --price 0.35 --quantity 100 --post-delay 1.0 --max-depth 12 --dialog-timeout 6 --confirm-timeout 3 --confirm-post-delay 1.0 --result-timeout 3 --close-result-dialog --result-close-pre-delay 0.5 --output pingan-submit-once-result.json
```

## 3. 预期结果

### 3.1 stderr 日志

应能看到一行：

```text
[pingan-buy-submit-once] contract_no=<合同号>
```

### 3.2 命令结果 JSON

打开 `pingan-submit-once-result.json`，确认至少存在下面字段：

```json
{
  "data": {
    "result_dialog": {
      "contract_no": "..."
    },
    "artifacts": {
      "last_order_state_path": "runtime/pingan-last-order.json"
    }
  }
}
```

### 3.3 固定状态文件

打开 `runtime/pingan-last-order.json`，确认至少存在下面字段：

```json
{
  "ok": true,
  "contract_no": "...",
  "input": {
    "code": "516820"
  },
  "result_dialog": {
    "contract_no": "..."
  }
}
```

### 3.4 一致性检查

下面 3 处的合同号必须一致：

- stderr 日志中的 `contract_no`
- `pingan-submit-once-result.json` 中的 `data.result_dialog.contract_no`
- `runtime/pingan-last-order.json` 中的 `contract_no`

## 4. 异常判定

出现下面任一情况，都视为本轮未通过：

- 结果窗未出现
- 结果窗出现但未自动关闭
- 主界面未恢复，无法继续下一单
- JSON 中 `contract_no` 为空
- 状态文件未生成
- 三处合同号不一致

## 5. 建议补充留档

每次验收建议保留下面材料：

- 本次命令 stderr 截图或日志文本
- `--output` 结果 JSON
- `runtime/pingan-last-order.json`
- 下单证券代码、价格、数量与执行时间
