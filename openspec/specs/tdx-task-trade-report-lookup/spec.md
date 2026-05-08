# tdx-task-trade-report-lookup Specification

## Purpose

定义单笔交易报告查询任务能力，稳定从连续任务流水解析匹配记录、关联报告产物，并提供调试追踪所需的结构化结果。

## Requirements

### Requirement: Task trade report lookup SHALL provide a stable workflow for resolving single trade reports from continuous ledgers
The system SHALL provide a stable task-facing workflow that reads continuous task ledger artifacts and resolves matching single-run report artifacts for debugging and traceability.

#### Scenario: Caller looks up a single report by contract number
- **WHEN** a caller provides a contract number that matches one ledger entry
- **THEN** the workflow MUST return the matching ledger entry, the linked report artifact paths, and the loaded JSON report content when available

#### Scenario: Caller looks up report candidates by stock code
- **WHEN** a caller provides a stock code instead of a contract number
- **THEN** the workflow MUST return matching candidate entries ordered from newest to oldest

#### Scenario: Caller exports lookup results
- **WHEN** a caller provides output paths for the report lookup workflow
- **THEN** the workflow MUST write the lookup result to structured export artifacts
