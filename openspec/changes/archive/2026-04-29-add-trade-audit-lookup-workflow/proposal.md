## Why

`trade_audit` 已经成为稳定桌面交易路径的正式产物，但当前还没有稳定入口去消费这些审计文件。日常排障仍然只能直接翻 `runtime/trade-audits/` 目录，不适合上层调用，也不利于后续补统一 report/catalog。

当前最小缺口不是做日报或多日聚合，而是先提供一个稳定的单次查询工作流：

- 按 `audit_id` 精确定位一条审计记录
- 按 `contract_no`、`submission_key`、`code` 查看候选记录
- 在唯一命中的情况下直接返回完整审计 JSON
- 保持 `task` / `report` 两层入口风格一致

## What Changes

- 新增稳定 task workflow：`TdxTaskManager.trade_audit_lookup(...)`
- 新增 CLI：
  - `task trade-audit-lookup`
  - `report audit-lookup`
- 新增 task/report 默认 profile 映射：
  - `trade_audit_lookup`
- 提供基于 `runtime/trade-audits/` 的目录扫描、过滤、排序和唯一命中加载
- 支持可选 JSON/CSV 导出

## Impact

- 新增 spec：`tdx-task-trade-audit-lookup`
- 更新 spec：
  - `tdx-task-management`
  - `tdx-report-cli-entry`
- 代码影响集中在：
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tdxquant/tasking.py`
  - `tdxquant/reporting.py`
  - `runtime/task-profiles.json`
