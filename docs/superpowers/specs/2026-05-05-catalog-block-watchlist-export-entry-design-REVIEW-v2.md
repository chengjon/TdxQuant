# Review v2: Catalog Block Watchlist Export Entry Design

Date: 2026-05-05

## Verdict: PASS

修订后的设计精准且可执行。上轮 9 项问题（P1–P9）全部得到有效回应，且落地路径已与代码现状对齐。

---

## 上轮问题回应验证

| 上轮问题 | 修订方案 | 验证 |
|----------|---------|------|
| P1: entry shape 与现有 schema 不兼容 | Decision 1 明确复用现有 schema | PASS — 示例 entry 完全匹配 `command-catalog.json` 的 `source/preset/description/labels` 结构 |
| P2: 大部分能力已实现 | Context 段明确承认现有基础设施 | PASS — 列出了 `catalog.py`、CLI 命令、registry 文件 |
| P3: `summary` 引入数据冗余 | Decision 5 明确不内联 preset 参数 | PASS — 需查看参数时走 `catalog plan` |
| P4: `catalog show` 定义不足 | Decision 3 明确不新增 `show`，复用 `list --entry` | PASS — 语义等价，无额外工作 |
| P5: 未提及 `catalog plan` | Decision 4 显式包含 `plan` | PASS — 与现有 CLI 能力一致 |
| P6: `kind` 字段冗余 | 已移除 | PASS |
| P7: implementation surface 模糊 | 已映射到 `command-catalog.json` + `tests/test_api_cli.py` | PASS |
| P8: test boundaries 未参考现有测试 | 收窄为增量 regression | PASS |
| P9: error semantics 遗漏已有校验 | Error semantics 段列出已有校验路径 | PASS |

---

## 代码验证

以下对设计中每个关键断言做了代码对照：

### 1. 现有 schema 校验逻辑

`catalog.py:resolve_command_catalog_entry()` 要求 `source` 和 `preset` 为非空字符串，且 `source ∈ {"report", "task", "trade"}`。

设计的示例 entry `source: "task"`, `preset: "export-zxg-watchlist"` 完全满足。

### 2. Preset 已存在

`runtime/task-presets.json` 中 `export-zxg-watchlist` 已定义，`command: "block-read-watchlist-export"`，包含 `block_code`, `export_output`, `overwrite` 三个 options。

### 3. `TASK_COMMAND_DEFAULT_PROFILES` 已包含该命令

`tasking.py:18` — `"block-read-watchlist-export": "default"` 已在 registry 中。preset 解析链不会因缺 profile 而失败。

### 4. CLI dispatch 链完整

`cli.py` 中 task-source catalog 的 dispatch 路径：

```
catalog run --entry <name>
  → _dispatch_catalog_resolved_entry(source="task", preset=<preset>)
    → _build_catalog_dispatch_namespace → {command="task", task_command="run", preset=<preset>}
      → _handle_task_subcommand
        → _build_task_preset_namespace
          → resolve_task_preset("export-zxg-watchlist")
            → 校验 block_code + export_output (cli.py:3600-3602)
              → manager.block_read_watchlist_export(...)
```

全链路无需新增代码，只需新增 catalog entry。

### 5. 测试模式对齐

`tests/test_api_cli.py` 已有 `test_catalog_list_command_parses`, `test_catalog_run_command_parses` 等模式。设计的测试边界遵循同一结构，只做增量覆盖。

---

## Remaining Notes (非阻塞)

以下观察不影响设计的可执行性，仅作记录：

### N1: `catalog list` 默认行为应隐式验证

设计说 "`catalog list` 能看到 `export-zxg-watchlist`"。`catalog list` 默认 `--kind entry`，列出所有 entry。新增 entry 后它自然出现，但测试中仍应有一条显式断言验证该 entry 在未过滤列表中可见，而不仅仅在 `--entry` 过滤后可见。

### N2: `catalog plan` 的 `resolved_args` 输出依赖 preset namespace 合并逻辑

`catalog plan` 通过 `_build_catalog_resolved_execution_namespace` 构建最终 namespace，会经历 preset options 合并。测试应验证 `resolved_args` 中包含正确的 `block_code`、`export_output`、`overwrite` 值，确保 preset options 到 namespace 的映射在 task source 路径上工作正常。

### N3: 未来多 block export preset 的命名约定

当前只有 `export-zxg-watchlist` 一个 preset。如果后续新增 `export-other-watchlist`，catalog entry 命名应保持一致的 `export-<block>-watchlist` 模式。这一点不需要现在约束，但作为设计文档的延续性观察记录在此。

---

## Summary

修订后的设计在以下方面表现优秀：

- **范围精准**: 实质改动仅为一条 JSON entry + 增量测试
- **代码对齐**: 每个断言都能在现有代码中找到对应实现
- **不做多余的事**: 不新增 schema、不新增命令、不内联参数、不重复校验
- **测试边界清晰**: 只验证增量，不重复覆盖已有路径

**建议直接进入 implementation。**
