# Design Review: task-block-read-full

Reviewer: Claude Opus 4.7
Date: 2026-05-05
Document: `docs/superpowers/specs/2026-05-05-task-block-read-full-design.md`

---

## Overall Assessment

设计定位清晰，边界克制，方案选择合理。Approach A 完全符合现有 codebase 的 task-wrapper 惯例。以下按类别列出具体意见。

---

## 1. Strengths

- **边界定义精准**：Non-Goals 列表明确排除了 batch / export / write / raw rows / 二次读取，有效防止 scope creep。
- **方案选择正确**：Approach A 与现有 `block_read_watchlist` 的 thin-wrapper 模式一致，task 层只做 enriched view 投影，不复制 provider 逻辑。
- **失败语义清晰**："不伪造 `data.read_full`" 是关键约束，避免半成功状态误导调用方。
- **独立命令 vs `--full` flag 的取舍分析合理**：保持 `block-read-watchlist` 作为 pure thin wrapper 不受污染。

---

## 2. Issues & Suggestions

### 2.1 `data.read_full` 字段存在冗余 [Medium]

`read_full` 中多个字段与 `snapshot` / `snapshot.source_metadata` 一一对应，只是做了平铺：

| read_full 字段 | 来源 |
|---|---|
| `block_code` | `snapshot.block_code` |
| `symbol_count` | `snapshot.symbol_count` |
| `source` | `snapshot.source` |
| `source_metadata` | `snapshot.source_metadata` (原样保留) |

这意味着调用方完全可以直接从 `snapshot` 读取这些值。`read_full` 真正新增的信息只有：

- `sector_name` (从 `source_metadata` 提升一级)
- `raw_member_count` (从 `source_metadata` 提升一级)
- `duplicate_count` (从 `source_metadata` 提升一级)
- `warnings_present` (从 `warnings` 派生)

**建议**：考虑是否真的需要平铺全部字段，还是只提供 `data.read_full` 作为 **diagnostics summary**，即只放 `read_full` 独有计算的派生字段，引用 `snapshot` 作为 source of truth。这样可以避免两个位置持有相同数据，长期维护时减少同步负担。

如果确定要平铺（为了消费方不需要回查 snapshot），建议在文档中补充一句设计意图说明。

### 2.2 Response Shape 描述需补充 manager-layer 元数据 [Low]

文档 Section 3 列出的成功响应字段：

```
- success/code/message
- warnings
- artifacts
- data.snapshot
- data.read_full
- data.task
- data.task_profile
- data.timing
```

但根据现有 codebase，`_attach_task_metadata` 追加的是 `task` / `task_profile` / `timing`，而 manager-layer `attach_manager_metadata` 还会追加：

- `data.manager`
- `data.api_profile`
- `data._provider_contract`（可能）

另外 `artifacts` 在当前 `block_read_watchlist` task 中并不存在——它是 `Result` 的 provider-level 序列化字段，task 层并未显式设置。

**建议**：明确 `artifacts` 是否会在 `block-read-full` 中设置。如果不会，从列表中移除，避免误导。

### 2.3 缺少 `data.read_full` 的空值/边界场景说明 [Medium]

文档只描述了两种状态：

1. 底层成功 → 生成 `read_full`
2. 底层失败 → 不生成 `read_full`

但缺少对以下边界场景的说明：

- **snapshot 成功但 `source_metadata` 为空或缺少预期字段**（如 `sector_name`、`raw_member_count`、`duplicate_count`）时，`read_full` 中的对应字段应该是什么？`None`？空字符串？还是整个 `read_full` 降级为不生成？
- **snapshot 成功但 `symbols` 为空列表**（block 存在但无成员）时，`read_full` 是否正常生成？

**建议**：补充一段 "Degraded Snapshot Handling"，明确 `source_metadata` 字段缺失时的 fallback 策略。建议至少区分：
- 可选字段缺失 → 设为 `None`，仍生成 `read_full`
- 必需字段（如 `block_code`）缺失 → 视为异常，不生成 `read_full`

### 2.4 CLI Contract 未提及 `--output` 的处理 [Low]

文档 Section 2 明确不支持 `--output`，Section 5 CLI 示例也没有。但现有 `_add_task_common_arguments` 自动包含了 `--output` 参数。

**建议**：明确说明 CLI 注册时是使用 `_add_task_common_arguments`（会自动带 `--output`）还是手动声明参数列表。如果使用 common arguments，需说明 `--output` 在此命令中是被忽略还是报错。参考 `block-read-watchlist` 的实际行为。

### 2.5 Testing Section 缺少 `read_full` 字段级断言 [Medium]

测试章节列出了要覆盖的场景（调用、成功、失败），但没有提到对 `data.read_full` 各字段的断言。

**建议**：至少补充：

- 成功时 `read_full.block_code == snapshot.block_code`
- 成功时 `read_full.sector_name == snapshot.source_metadata.sector_name`
- 成功时 `read_full.warnings_present == (len(warnings) > 0)`
- 成功时 snapshot 字段完整但 `source_metadata` 部分缺失的场景（见 2.3）

### 2.6 缺少 Preset 注册说明 [Low]

现有 `block-read-watchlist-export` 在 `tasking.py` 的 `TASK_COMMAND_DEFAULT_PROFILES` 中有注册。新命令是否需要注册？

**建议**：如果 `block-read-full` 需要支持 preset profile，补充 preset 注册说明。如果第一版不需要，在 Non-Goals 中明确。

---

## 3. Minor Nits

- **Section 3**："顶层继续沿用现有 provider envelope 与 task metadata 约定" —— task 层返回的是 `Result`，不直接暴露 provider envelope。建议改为 "沿用现有 `Result` envelope 与 task metadata 约定"。
- **Section 4**："直接透传底层失败"措辞准确，但可补充一句："task 层不 catch/re-raise，不转换 error code"。

---

## 4. Summary

| 类别 | 数量 |
|---|---|
| 需要回应的 Issue | 6 |
| High | 0 |
| Medium | 3（字段冗余、边界场景、测试断言） |
| Low | 3（元数据描述、CLI output、Preset） |

**结论**：设计整体质量好，方向正确。主要建议集中在 `read_full` 的字段设计是否需要更精简、以及补充边界场景处理策略。建议在开始实现前回应 Medium 级别的 3 个问题。
