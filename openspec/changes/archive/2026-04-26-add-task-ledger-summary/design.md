## Context

当前 task 层已经能为 `guarded_trade_buy` 自动生成：

- 单次 JSON 报告
- 单次 CSV 摘要
- 连续 JSONL 台账
- 连续 CSV 台账

问题不在产出，而在消费。调用方如果想知道最近 10 次执行情况、某个代码的历史记录、某个合同号对应哪次报告，仍然需要自己读文件并做筛选。

## Goals / Non-Goals

**Goals:**

- 为 task 层提供稳定的 ledger summary workflow。
- 优先消费现有 JSONL 台账，必要时回退到 CSV。
- 输出结构化摘要、最近记录和可选导出文件。
- 保持与现有 task/profile/artifact 习惯一致。

**Non-Goals:**

- 不引入数据库或复杂统计引擎。
- 不修改桌面交易执行逻辑。
- 不做跨多个 ledger 的聚合分析平台。

## Decisions

### 1. 采用 task manager 新方法，而不是单独脚本

把 ledger 消费纳入 `TdxTaskManager`，这样：

- CLI、Python 调用和 profile 体系保持一致
- 输出继续使用统一 `Result` 模型
- 后续更容易把 ledger workflow 纳入更高层 task 编排

### 2. 以 JSONL 为主，CSV 为回退

JSONL 保留了更完整的数据类型和字段结构，适合程序消费；CSV 只作为缺少 JSONL 时的兼容读取来源。这样可以避免为 CSV 恢复复杂嵌套结构。

### 3. 摘要围绕“日常复盘”而不是“报表系统”

首版只提供：

- 总记录数
- 命中过滤后的记录数
- 成功/失败数量
- 最近时间戳
- 最近若干条记录

这已经足够覆盖日常核对、排障和后续人工追踪。

### 4. 导出当前筛选结果，而不是另建新报表模型

如果调用方需要保存当前视图，就直接把过滤后的结果导出为 JSON/CSV。这样实现简单，也能保持与已有 export task 风格一致。

## Risks / Trade-offs

- [CSV 数据类型退化] → 优先读取 JSONL，只在 JSONL 不存在时使用 CSV。
- [历史 ledger 字段可能不完全一致] → 摘要逻辑按容错方式读取字段，缺字段时返回空值而不是失败。
- [记录很多时读取全文件会变慢] → 首版先保持简单实现；如果后续 ledger 规模明显增大，再补增量读取或 tail 优化。
