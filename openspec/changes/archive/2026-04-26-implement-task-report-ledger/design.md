## Context

`guarded_trade_buy` 已经输出：

- 单次 JSON 报告
- 单次 CSV 摘要

但这些文件本身不提供历史串联关系。既然 task 层已经是最上层 workflow 入口，连续索引就应在这里自动维护。

## Goals

- 每次 guarded trade 执行时自动维护连续索引。
- 索引内容足够轻量，便于人工查看和程序消费。
- 不破坏现有单次报告结构。

## Non-Goals

- 本次不做专门的查询命令。
- 本次不做数据库或复杂统计。

## Decisions

### 1. 同时维护 JSONL 和 CSV 台账

- JSONL 适合保留结构化上下文
- CSV 适合快速肉眼查看和表格处理

### 2. 只先覆盖 guarded trade 模板

先从 `guarded_trade_buy` 开始，避免所有 task 一起改动。后续如果效果稳定，再扩展到更多 workflow。

### 3. 台账记录最小关键字段

至少记录：

- 时间戳
- task 名
- code / price / quantity
- snapshot / block / formula 检查结果
- trade ok
- contract_no
- 单次 JSON/CSV 报告路径

## Verification

- task manager 测试验证台账文件追加。
- 回归测试验证既有单次报告行为不回退。
