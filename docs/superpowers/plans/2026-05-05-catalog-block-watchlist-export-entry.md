# Catalog Block Watchlist Export Entry Implementation Plan

## Goal

把现有 `block-read-watchlist-export` preset 接进现有 `catalog` 体系，让：

- `catalog list`
- `catalog list --entry export-zxg-watchlist`
- `catalog run --entry export-zxg-watchlist`
- `catalog plan --entry export-zxg-watchlist`

能够在**不修改 catalog schema、不新增 catalog 子命令**的前提下工作。

## Scope

### In scope

- 在 `runtime/command-catalog.json` 新增一条兼容现有 schema 的 task-source entry
- 为该 entry 补 focused CLI regression
- 必要时补 usage docs / roadmap docs

### Out of scope

- 新增 catalog schema
- 新增 `catalog show`
- 修改 `tdxquant/catalog.py` 的 schema 规则
- 修改 `catalog run/plan` 的核心 dispatch 逻辑，除非 focused tests 暴露真实缺口
- provider / task / preset 行为扩展

## Workstreams

## 1. Catalog registry entry

### 1.1 Add a task-source entry to `runtime/command-catalog.json`

新增一条最小兼容 entry：

```json
"export-zxg-watchlist": {
  "source": "task",
  "preset": "export-zxg-watchlist",
  "description": "Export ZXG watchlist snapshot to a fixed JSON path.",
  "labels": ["task", "block", "watchlist", "export"]
}
```

要求：

- 复用现有 schema：
  - `source`
  - `preset`
  - `description`
  - `labels`
- 不内联：
  - `block_code`
  - `export_output`
  - `overwrite`

### 1.2 Verify no extra catalog metadata is required

先依赖现有：

- `resolve_command_catalog_entry(...)`
- `_resolve_catalog_preset_metadata(...)`
- `_build_catalog_dispatch_namespace(...)`

如果 focused tests 证明现有流程已经足够，则不修改 catalog 内核。

## 2. Focused CLI regression

### 2.1 Cover default entry listing visibility

在 `tests/test_api_cli.py` 增加 focused test，验证：

- 默认 `catalog list` 的未过滤 entry 列表中包含 `export-zxg-watchlist`

### 2.2 Cover single-entry inspection

验证：

- `catalog list --entry export-zxg-watchlist`
  能返回这条 entry

### 2.3 Cover plan path

验证：

- `catalog plan --entry export-zxg-watchlist`
  能展示解析后的 `resolved_args`

至少断言：

- `block_code`
- `export_output`
- `overwrite`

### 2.4 Cover run dispatch

验证：

- `catalog run --entry export-zxg-watchlist`
  能正确委派到现有：
  - `task run --preset export-zxg-watchlist`

### 2.5 Cover failure paths only if the new entry surfaces gaps

只在新增 entry 真实暴露缺口时补：

- preset missing
- invalid source mapping

不为了这条线重复覆盖 catalog 既有错误语义。

## 3. Documentation sync

### 3.1 Update user-facing usage docs if needed

如果当前 usage 文档已有 catalog 章节，则补一小段：

- 通过 catalog 发现 block watchlist export entry
- 通过 `catalog plan/run` 使用该 entry

### 3.2 Update roadmap / function map if needed

仅在现有文档明确列出 catalog 缺口时补最小同步说明。

## 4. Verification

### 4.1 Focused regression

至少运行：

```bash
python -m pytest tests/test_api_cli.py -k "catalog and export_zxg_watchlist" -q
```

如果命名不同，则以实际新增测试名为准。

### 4.2 Broader catalog sanity

再跑一组较宽的 catalog 相关回归，例如：

```bash
python -m pytest tests/test_api_cli.py -k "catalog" -q
```

### 4.3 Diff hygiene

在最终声称完成前确认：

```bash
git diff --check
```

如果 repo-wide 仍有既有脏问题，则至少对本次变更文件单独检查 clean。

## Expected changed files

最理想情况下只会改：

- `runtime/command-catalog.json`
- `tests/test_api_cli.py`
- 可选：
  - `runtime/TdxQuant_Task_Layer_Usage.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`

原则上不应改：

- `tdxquant/catalog.py`
- `tdxquant/cli.py`

除非 focused tests 证明现有 catalog/preset 投射链存在真实缺口。

## Completion criteria

这条线完成时应满足：

1. `command-catalog.json` 新增了 `export-zxg-watchlist` task-source entry
2. 现有 `catalog list/run/plan` 能消费该 entry
3. focused CLI tests 通过
4. 没有无必要地扩大到 catalog schema 或 dispatch 重构
