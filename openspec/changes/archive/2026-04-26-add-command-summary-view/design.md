## Context

当前 catalog 已支持：

- `list`
- `run`
- `plan`
- bundle step 选择
- label 过滤

但 `run` / `plan` 输出仍然是面向诊断的完整结果结构，不够适合高频终端查看。

## Goals / Non-Goals

**Goals:**

- 保持完整 JSON 作为默认行为。
- 为 `catalog run` / `catalog plan` 增加 opt-in 的 summary 视图。
- summary 视图能快速表达 entry/bundle、状态、范围、关键字段。

**Non-Goals:**

- 不修改 list 输出。
- 不修改执行逻辑或 result 对象内部结构的主语义。
- 不做终端彩色渲染或表格排版。

## Decisions

### 1. 采用 `--view detailed|summary`

在 `catalog run` 和 `catalog plan` 上增加：

- `--view detailed`
- `--view summary`

默认 `detailed`，保持兼容。

### 2. handler 负责构造 `summary_view`

`_handle_catalog_subcommand()` 返回的 `Result.data` 中新增：

- `summary_view`

这样：

- `main()` 只决定打印 `result.to_dict()` 还是 `result.data["summary_view"]`
- tests 可以直接验证 handler 产出的 summary 数据

### 3. summary view 只保留高信号字段

entry run summary：

- `mode`
- `target`
- `ok` / `code` / `message`
- `dispatch`
- 关键输入字段（如 `code`、`price`、`quantity`、`date`、`contract_no`）
- `contract_no`

bundle run summary：

- `mode`
- `target`
- `ok` / `code` / `message`
- 选中范围
- 每个 step 的 `index` / `name` / `entry` / `ok` / `code` / `message`
- `trade_contract_no`

plan summary 只保留：

- `mode`
- `target`
- `dispatch` 或 `steps`
- 关键 resolved args

### 4. summary 输出只影响最终序列化

内部执行、日志、输出文件写入路径、退出码都仍基于完整 `Result`。summary 只是最终打印/写出的视图。

## Risks / Trade-offs

- [summary 字段选择主观] → 先保留最稳定、最常用的字段，后续可再补。
- [handler 多一层摘要构造] → 通过独立 helper 控制，避免散落在 `main()`。
