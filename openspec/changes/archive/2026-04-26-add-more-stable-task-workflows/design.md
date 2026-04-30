## Context

`TdxTaskManager` 当前已经验证了三类基础编排：

- `sector_research`
- `formula_scan`
- `refresh_environment`

但其中 `sector_research` 偏研究视角，`formula_scan` 需要调用方自己准备代码列表。为了更贴近日常使用，需要补两条更自然的入口：

- 手头已经有代码列表时，快速看一眼批量指标或总览数据
- 手头只有板块时，直接完成“成分提取 + 公式扫描”

## Decisions

### 1. `watchlist_overview` 复用 `meta.gp_one_data`

这个任务接收明确的代码列表和字段列表，直接调用：

- `manager.meta.gp_one_data(...)`

它不做额外业务判断，作用是把“多代码总览”从原子 API 提升为稳定 task。

### 2. `sector_formula_scan` 复用 `meta.sector_stocks + formula.process_mul_xg`

这个任务先取板块成分，再把提取出的代码喂给公式扫描：

1. `manager.meta.sector_stocks(...)`
2. 提取 `stock_codes`
3. `manager.formula.process_mul_xg(...)`

这样可以把“板块到扫描结果”的固定流程收敛成一个 task。

### 3. 两个新增任务继续遵循 task 层边界

- 不直接调用 `bridge.py`
- 不覆盖桌面交易
- 不隐藏关键参数
- 保持 JSON 结果和 task 元数据一致性

## Risks / Trade-offs

- `watchlist_overview` 仍依赖底层 `gp_one_data` 返回结构
- `sector_formula_scan` 依赖板块成分结果里能稳定提取证券代码
- 当前仍不做 CSV 导出，只保留结构化 JSON 输出

## Delivery

本次只新增稳定 task，不引入新的 manager 域，也不扩展桌面交易能力。
