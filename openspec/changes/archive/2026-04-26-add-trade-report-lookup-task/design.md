## Context

当前 ledger 条目已经包含：

- `contract_no`
- `code`
- `report_json_path`
- `report_csv_path`

这说明定位单次报告所需的索引数据已经存在，只是还没有稳定的 task 封装来消费它。现在用户如果想定位一笔交易，仍然要自己查 ledger、复制路径、再打开对应文件。

## Goals / Non-Goals

**Goals:**

- 提供一个稳定的 `trade_report_lookup` task。
- 支持按合同号精确定位，按代码/日期做候选筛选。
- 返回 ledger 条目、报告路径、文件存在性状态。
- 在唯一命中且 JSON 报告存在时，直接把报告内容加载进结果。

**Non-Goals:**

- 不做新的统计报表。
- 不修改已有交易执行或 ledger 写入逻辑。
- 不做 GUI 打开文件动作。

## Decisions

### 1. 合同号优先，代码查询作为候选模式

`contract_no` 是最稳定的单次交易标识，应作为精确回溯入口。`code` 则更适合返回候选记录列表，必要时再结合日期或任务名收敛。

### 2. 继续复用 ledger source 与过滤 helper

本次不重新发明一套读取逻辑，而是直接在 `ledger_summary` / `daily_trade_report` 已有 helper 基础上叠加单次回溯行为，减少分叉实现。

### 3. 只在唯一命中时自动加载 JSON 报告

如果命中多条记录，自动加载所有报告会让结果膨胀且不稳定。唯一命中时自动读取 JSON 报告，已经能满足最常见的排障路径；多条命中时只返回候选路径和元信息。

### 4. 返回路径状态，而不是假设文件一定存在

ledger 指向的报告文件理论上应存在，但实际使用中可能被移动或清理。因此 task 返回中要明确暴露 `report_json_exists` / `report_csv_exists`，便于区分“索引存在”和“产物仍在”。

## Risks / Trade-offs

- [历史 ledger 条目可能缺少路径字段] → 返回空路径和不存在状态，而不是任务失败。
- [按代码查询可能命中很多记录] → 提供 `limit` 与日期过滤，默认只返回最近若干条。
- [报告 JSON 文件内容可能损坏] → 文件读取失败时保留路径信息，并在结果中返回警告，而不是让整个 lookup 失败。
