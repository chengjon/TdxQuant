# Review: Catalog Block Watchlist Export Entry Design

Date: 2026-05-05

## Overall

设计意图清晰：让 `block-read-watchlist-export` 的 preset-backed 入口能被 catalog 发现和触发。核心判断（catalog 只做 preset 视图层）与现有代码架构一致。

但设计文档提出的 entry shape 与现有 catalog 基础设施存在明显脱节，且未充分利用已经实现的能力。以下分项说明。

---

## P1: Entry shape 与现有 catalog schema 不兼容

**现状**: `command-catalog.json` 的每条 entry 必须包含 `source` 和 `preset` 字段，且 `source` 必须属于 `SUPPORTED_COMMAND_CATALOG_SOURCES = {"report", "task", "trade"}`。校验逻辑在 `catalog.py:resolve_command_catalog_entry()` 中硬编码。

**设计提案**: entry 使用 `entry_id`, `kind`, `preset_name`, `command`, `title`, `description`, `summary` 字段。

**问题**: 设计提出的字段集合与现有 schema 完全不匹配：
- 没有 `source` 字段 → `resolve_command_catalog_entry` 会拒绝
- 用 `preset_name` 而非 `preset` → 校验失败
- 新增 `kind`, `command`, `title`, `summary` → 现有 loader 忽略但不校验

**建议**: 如果 V1 目标是最小增量，应直接复用现有 catalog schema，只需在 `command-catalog.json` 中新增一条 task-source entry：

```json
{
  "export-zxg-watchlist": {
    "source": "task",
    "preset": "export-zxg-watchlist",
    "description": "Export ZXG watchlist snapshot to a fixed JSON path.",
    "labels": ["task", "block", "watchlist", "export"]
  }
}
```

如果确实需要新 schema，则需要：
- 在 `catalog.py` 中新增 schema 版本识别和迁移逻辑
- 更新 `resolve_command_catalog_entry` 的校验规则
- 对现有所有 entry 做向后兼容验证

这两种路线的工作量差一个数量级，设计文档应明确选择哪一条。

---

## P2: 大部分能力已经实现

设计文档把 `catalog list`, `catalog show`, `catalog run` 当作需要实现的能力描述，但实际上：

- `catalog list --entry` 已经工作，能列出所有 `command-catalog.json` 中的 entry
- `catalog run --entry <name>` 已经工作，对于 task source 会委派到 `task run --preset <preset>`
- `catalog plan --entry <name>` 已经工作，能做 dry-run 展示 resolved args
- preset `export-zxg-watchlist` 已经存在于 `task-presets.json`

也就是说，**唯一缺少的实质改动是往 `command-catalog.json` 加一条 JSON entry**。

设计文档应明确承认这一现状，把范围收窄到"新增一条 catalog entry 并验证端到端流程"，而不是重新描述已有能力。

---

## P3: `summary` 字段引入数据冗余

设计为 entry 新增了 `summary` 子对象，包含 `block_code`, `export_output`, `overwrite`。

**问题**: 这些值已经在 `task-presets.json` 的 `export-zxg-watchlist.options` 中定义。在 catalog entry 中重复一份意味着：
- 修改 preset 参数时必须同步更新 catalog entry
- 两份数据可能不一致
- 没有说明以哪份为准

**建议**: V1 不在 catalog entry 中内联 preset 参数。`catalog show` 如需展示这些信息，应在运行时从 preset 中解析后返回，而不是静态存储在 catalog entry 中。现有的 `catalog plan` 已经能展示 resolved args，可以复用。

---

## P4: `catalog show` 定义不足

设计新增了 `catalog show <entry_id>` 操作，但：

- 没有与现有 `catalog list --entry <name>` 做区分。当前 `catalog list --entry export-zxg-watchlist` 已经能返回单条 entry 的详细信息。
- 没有定义输出格式
- 没有说明是否需要新的 CLI subparser

**建议**: 如果 `show` 的语义与 `list --entry` 等价，V1 不需要新增命令。如果 `show` 要展示 preset 解析后的完整参数，则应明确说明输出 contract 并映射到 `catalog plan` 或类似机制。

---

## P5: 未提及 `catalog plan`

现有 CLI 已经支持 `catalog plan --entry <name>`，功能是 dry-run 展示解析后的 namespace。这是 catalog 层最有价值的诊断入口之一。

设计文档只提到 `list`, `show`, `run` 三种操作，完全没有提及 `plan`。

**建议**: 明确 `catalog plan` 是否在新 entry 上可用（如果复用现有 schema 则自动可用），或者在 Non-Goals 中说明理由。

---

## P6: `kind = "task_preset"` 的必要性不明确

设计引入了 `kind` 字段，取值 `"task_preset"`。

**问题**: 现有 catalog 已经通过 `source` 字段区分来源类型（`"report"`, `"task"`, `"trade"`）。对于 task source 的 entry，preset 是唯一的执行模型。新增 `kind` 字段解决的问题是什么？

**建议**: 如果 V1 所有 task-source entry 都是 preset-backed，则 `kind` 冗余。如果有 future plan 需要区分 task-preset vs task-direct 等类型，应在文档中说明演进路径。

---

## P7: Implementation surface 过于模糊

设计提出的 implementation surface 包括：

- "catalog registry / loader"
- "preset-backed entry projection"

这些没有映射到具体的文件或函数。实际上：

- `catalog registry / loader` = `tdxquant/catalog.py` + `runtime/command-catalog.json`
- `preset-backed entry projection` = 已在 `cli.py:_resolve_catalog_preset_metadata` 和 `_build_catalog_dispatch_namespace` 中实现

**建议**: 把 implementation surface 映射到具体文件和函数，明确哪些是新增、哪些是已有、哪些需要修改。

---

## P8: Test boundaries 应参考现有测试

设计提出的测试边界合理，但没有参考现有 catalog 测试模式。现有 `tests/test_api_cli.py` 中已有 catalog list/run 的测试用例。

**建议**: 新增测试应遵循现有测试结构，并且只需覆盖"新增 entry 能被现有 catalog list/run/plan 正确发现和执行"这一增量。

---

## P9: Error semantics 遗漏了 catalog 层已有的校验

设计定义了 4 种错误场景，但遗漏了现有 catalog 已经处理的场景：

- entry 的 `source` 不在 `SUPPORTED_COMMAND_CATALOG_SOURCES` 中 → `ValueError`
- entry 缺少 `source` 或 `preset` → `ValueError`
- preset 解析失败（preset 不存在于对应 source 的 preset 文件中）→ 错误

如果复用现有 schema，这些错误路径已经覆盖。

---

## Summary

| 严重度 | 问题 | 建议 |
|--------|------|------|
| P1 | entry shape 与现有 schema 不兼容 | 明确选择：复用现有 schema 或规划 schema 迁移 |
| P2 | 大部分能力已实现 | 收窄范围到新增 JSON entry |
| P3 | `summary` 引入数据冗余 | V1 不内联 preset 参数，运行时解析 |
| P4 | `catalog show` 与 `catalog list --entry` 未区分 | 明确区分或复用已有命令 |
| P5 | 未提及 `catalog plan` | 明确是否可用或说明理由 |
| P6 | `kind` 字段必要性不明确 | 如无演进 plan 则移除 |
| P7 | implementation surface 未映射到具体代码 | 映射到文件和函数 |
| P8 | test boundaries 未参考现有测试模式 | 遵循现有测试结构 |
| P9 | error semantics 遗漏已有校验场景 | 承认现有覆盖 |

**结论**: 设计的核心判断正确（catalog 只做 preset 视图层），但落地路径与现有代码现状脱节。如果 V1 目标是最小增量，实际上只需要：

1. 在 `runtime/command-catalog.json` 新增一条 `export-zxg-watchlist` entry（复用现有 schema）
2. 补充端到端测试验证 `catalog list/run/plan` 对该 entry 的工作
3. 更新 usage docs

建议在修订设计中明确选择这条路线，或者如果确实需要新 schema，则补充迁移策略和向后兼容性分析。
