# tdx-task-daily-trade-report Specification

## Purpose

定义日级交易报告任务能力，稳定读取连续任务流水，按本地交易日过滤、聚合并输出可机器消费的日报 JSON 与 CSV 视图，支持默认日期和显式交易日期两种调用方式。

## Requirements

### Requirement: Task daily trade report SHALL provide a stable day-level ledger aggregation workflow
The system SHALL provide a stable task-facing workflow that reads continuous task ledger artifacts, filters entries by local trade date, and returns structured daily aggregation data.

#### Scenario: Caller generates report for the default local trade date
- **WHEN** a caller runs the daily trade report workflow without explicitly providing a report date
- **THEN** the workflow MUST generate the report using the current date in the configured local timezone

#### Scenario: Caller generates report for a specific trade date
- **WHEN** a caller provides an explicit report date and timezone
- **THEN** the workflow MUST filter ledger entries using that local-date boundary before aggregation

#### Scenario: Caller exports the daily trade report
- **WHEN** a caller provides output paths for the daily trade report workflow
- **THEN** the workflow MUST write a structured JSON report and a CSV aggregation view
