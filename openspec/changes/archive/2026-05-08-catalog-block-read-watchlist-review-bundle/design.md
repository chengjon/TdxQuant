## Context

现有 block 读侧 catalog 基础设施已经具备：

- task-source entries:
  - `read-zxg-watchlist`
  - `read-zxg-full`
- bundle loader and resolver:
  - `runtime/command-bundles.json`
  - `tdxquant/catalog.py:resolve_command_bundle(...)`
- existing bundle UX:
  - `catalog list --kind bundle`
  - `catalog list --bundle <name>`
  - `catalog plan --bundle <name>`
  - `catalog run --bundle <name>`

因此，这条 change 的工作不是设计新的 bundle 模型，而是把 `read-zxg-review` 接进现有 bundle 体系，并把 bundle-level `--block-code` fanout 语义正式写回 contract。

## Goals / Non-Goals

**Goals**

- 正式定义 `read-zxg-review` 为稳定 catalog bundle。
- 明确该 bundle 继续复用现有 `command-bundles.json` schema。
- 明确 `catalog plan/run --bundle read-zxg-review --block-code <value>` 会统一覆盖两个 step 的 `block_code`。
- 明确 step 1 失败时 bundle 立即停止，不继续执行 step 2。

**Non-Goals**

- 不修改 catalog schema
- 不新增 bundle-level report/export/write-back
- 不新增每步独立参数覆盖
- 不修改底层 `block-read-watchlist` / `block-read-full` task contract

## Decisions

### 1. Reuse the existing command-bundles schema exactly

第一版 bundle 必须继续使用现有 schema：

- `description`
- `labels`
- `steps`
- `steps[].name`
- `steps[].entry`

不引入新的：

- `bundle_id`
- `step_args`
- `step_overrides`
- inline parameter definitions

### 2. The bundle is a pure read orchestration layer

`read-zxg-review` 的职责只有：

1. 先执行 `read-zxg-watchlist`
2. 再执行 `read-zxg-full`

因此：

- 它不新增 provider capability
- 它不新增 task result schema
- 它只复用现有 preset-backed catalog entry dispatch

### 3. Bundle-level `--block-code` fans out to both steps

V1 显式要求：

- `catalog plan --bundle read-zxg-review --block-code MYZXG`
- `catalog run --bundle read-zxg-review --block-code MYZXG`

都必须把 `MYZXG` 统一传给：

- step 1 → `read-zxg-watchlist`
- step 2 → `read-zxg-full`

这要求 `tdxquant/cli.py:_add_catalog_run_arguments(...)` 明确接受 `--block-code`，而不是只依赖现有 entry-only 参数集合。

### 4. Fail-fast execution remains unchanged

V1 继续复用现有 bundle 执行语义：

- step 1 失败 → bundle 立即停止
- 不继续执行 step 2
- 不发明第二套 bundle error model

## Risks / Trade-offs

- [把 bundle 做成新参数模型] → 通过继续复用现有 schema 和 top-level `--block-code` fanout 规避。
- [在 bundle 中重复定义 preset 默认参数] → 通过只引用既有 entry 名称规避。
- [让 bundle 自己重塑 task 结果] → 通过继续复用现有 dispatch 和 bundle result 形状规避。

## Migration Plan

1. 在 `tdxquant/cli.py` 给 `_add_catalog_run_arguments(...)` 增加 `--block-code`，并锁 parser/summary view 行为。
2. 在 `runtime/command-bundles.json` 新增 `read-zxg-review`，并用 focused CLI tests 锁住：
   - default bundle listing visibility
   - `catalog list --bundle read-zxg-review`
   - `catalog plan --bundle read-zxg-review`
   - `catalog run --bundle read-zxg-review`
3. 在 focused tests 里锁住 bundle-level `--block-code` 对两个 step 的统一覆盖，以及 step 1 failure short-circuit。
4. 同步修正文档与主 spec：
   - `runtime/TdxQuant_Task_Layer_Usage.md`
   - `docs/TdxQuant_Project_Function_Map.md`
   - `docs/TdxQuant_Next_Steps.md`
   - `openspec/specs/tdx-command-catalog/spec.md`
5. 创建并归档 `catalog-block-read-watchlist-review-bundle` change lifecycle。

## Open Questions

- 无。V1 只 formalize 最小增量 bundle 和统一 `--block-code` fanout 语义。
