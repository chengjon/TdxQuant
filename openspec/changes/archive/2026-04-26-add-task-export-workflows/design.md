## Context

`TdxTaskManager` 当前已经有：

- `sector_research`
- `formula_scan`
- `watchlist_overview`
- `sector_formula_scan`
- `refresh_environment`

但这些任务的输出仍偏“交给调用方自己处理”。为了贴近日常使用，还需要一层稳定落地：

- 自动写 JSON 结果文件
- 自动写 CSV 行数据文件
- 支持 profile 里的默认导出目录

## Decisions

### 1. 导出任务复用现有稳定 task，而不是直接重写原子编排

新增导出任务应直接复用现有稳定 task：

- `watchlist_export` 复用 `watchlist_overview`
- `sector_research_export` 复用 `sector_research`

这样可以避免两套逻辑分叉。

### 2. 导出能力由 task 层本地负责，不下沉到 manager

文件落地属于场景化输出，不属于原子 API 管理能力，因此应留在 task 层。

manager 继续只负责：

- 原子调用
- profile
- timing
- 标准结果封装

task 继续负责：

- 场景编排
- 文件输出
- 导出目录约定

### 3. JSON + CSV 同时支持，但 CSV 采用保守通用行格式

由于底层返回结构并不完全统一，CSV 导出采用保守策略：

- 优先从任务结果中提取可序列化 dict 行
- 若无法稳定展开，则退化为包含 `stock_code` 和原始值的行

这样能保证功能先可用，再逐步细化。

### 4. profile 增加默认导出目录

task profile 增加导出相关默认值，例如：

- `export_dir`
- `export_stem`

调用方仍可通过 CLI 显式覆盖输出文件路径。

## Risks / Trade-offs

- CSV 行格式会受底层结果结构影响，短期内只能做到“通用可用”，未必是最精细格式
- 导出任务本质是 task 输出层增强，不应演化成复杂报表系统
- 当前只做本地文件落地，不做数据库或远程存储

## Delivery

本次只新增 task 导出能力，不新增 manager 域，不涉及桌面交易能力。
