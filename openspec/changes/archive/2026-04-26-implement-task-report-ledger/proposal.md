## Why

当前 `guarded_trade_buy` 已经会生成单次 JSON/CSV 报告，但这些产物还是“单次文件”形态。日常使用中更需要的是一个连续可追踪的台账，方便：

- 回看最近执行过哪些任务
- 快速定位某次交易的合同号、前置检查、结果文件
- 后续做统计、筛查和排障

现在需要为任务报告补一个自动维护的索引层。

## What Changes

- 为 `guarded_trade_buy` 增加任务台账索引产物。
- 每次执行时自动追加：
  - JSONL 台账
  - CSV 台账
- 在单次任务结果中返回台账文件路径。

## Capabilities

### Modified Capabilities

- `tdx-task-management`

## Impact

- 任务结果从“单次报告”升级为“单次报告 + 连续索引”。
- 后续可以直接基于台账做汇总、筛选和审计。
