## Context

现有 block 读侧 catalog 基础设施已经具备：

- task-source entries:
  - `read-zxg-watchlist`
  - `read-zxg-full`
  - `export-zxg-watchlist`
- bundle loader and resolver:
  - `runtime/command-bundles.json`
  - `tdxquant/catalog.py:resolve_command_bundle(...)`
- existing bundle UX:
  - `catalog list --kind bundle`
  - `catalog list --bundle <name>`
  - `catalog plan --bundle <name>`
  - `catalog run --bundle <name>`

因此，这条 change 的工作不是设计新的 bundle 模型，而是把 `read-zxg-review-and-export` 接进现有 bundle 体系，并把 bundle-level `--block-code` fanout 与 preset-owned export 参数边界正式写回 contract。

## Goals / Non-Goals

**Goals**

- 正式定义 `read-zxg-review-and-export` 为稳定 catalog bundle。
- 明确该 bundle 继续复用现有 `command-bundles.json` schema。
- 明确三步固定顺序为 `read-zxg-watchlist`、`read-zxg-full`、`export-zxg-watchlist`。
- 明确 `catalog plan/run --bundle read-zxg-review-and-export --block-code <value>` 会统一覆盖三步的 `block_code`。
- 明确 `export_output` 和 `overwrite` 继续由 `export-zxg-watchlist` preset 持有。
- 明确 step 2 失败时 bundle 在 export 前停止，step 3 失败时 bundle 返回失败。

**Non-Goals**

- 不修改 catalog schema
- 不新增 bundle-level `--export-output` 或 `--overwrite`
- 不新增每步独立参数覆盖
- 不新增 provider capability
- 不修改底层 `block-read-watchlist` / `block-read-full` / `block-read-watchlist-export` task contract

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

### 2. The bundle is a thin read-and-export orchestration layer

`read-zxg-review-and-export` 的职责只有：

1. 先执行 `read-zxg-watchlist`
2. 再执行 `read-zxg-full`
3. 最后执行 `export-zxg-watchlist`

因此：

- 它不新增 provider capability
- 它不新增 task result schema
- 它不新增 export pipeline
- 它只复用现有 preset-backed catalog entry dispatch

### 3. Bundle-level `--block-code` fans out to all three steps

V1 显式要求：

- `catalog plan --bundle read-zxg-review-and-export --block-code MYZXG`
- `catalog run --bundle read-zxg-review-and-export --block-code MYZXG`

都必须把 `MYZXG` 统一传给：

- step 1 -> `read-zxg-watchlist`
- step 2 -> `read-zxg-full`
- step 3 -> `export-zxg-watchlist`

这继续复用已经存在的 catalog bundle namespace 合并逻辑，不引入每步单独参数层。

### 4. Export output stays preset-owned

V1 明确不支持：

- `catalog plan --bundle ... --export-output ...`
- `catalog run --bundle ... --export-output ...`
- `catalog run --bundle ... --overwrite`

第三步 export 使用的输出路径和 overwrite 策略继续来自 `export-zxg-watchlist` preset。这避免了 bundle 顶层参数只被第三步消费的特殊规则。

### 5. Fail-fast execution remains unchanged

V1 继续复用现有 bundle 执行语义：

- step 1 失败 -> bundle 立即停止，不执行 step 2 / step 3
- step 2 失败 -> bundle 立即停止，不执行 step 3
- step 3 失败 -> bundle 返回失败
- 不发明第二套 bundle error model
- 不做回滚

## Risks / Trade-offs

- [把 bundle 做成新参数模型] -> 通过继续复用现有 schema 和 top-level `--block-code` fanout 规避。
- [在 bundle 中重复定义 export 默认参数] -> 通过只引用既有 entry 名称并保留 preset-owned `export_output` / `overwrite` 规避。
- [让 bundle 自己重塑 task 结果] -> 通过继续复用现有 dispatch 和 bundle result 形状规避。

## Migration Plan

1. 在 `runtime/command-bundles.json` 新增 `read-zxg-review-and-export`。
2. 用 focused CLI tests 锁住：
   - default bundle listing visibility
   - `catalog list --bundle read-zxg-review-and-export`
   - `catalog plan --bundle read-zxg-review-and-export`
   - `catalog run --bundle read-zxg-review-and-export`
   - bundle-level `--block-code` 对三步的统一覆盖
   - summary view 不暴露 preset-owned export controls
   - step 2 failure stop-before-export
   - step 3 export failure propagation
   - unsupported bundle-level export flags
3. 同步修正文档与主 spec：
   - `runtime/TdxQuant_Task_Layer_Usage.md`
   - `docs/TdxQuant_Project_Function_Map.md`
   - `docs/TdxQuant_Next_Steps.md`
   - `openspec/specs/tdx-command-catalog/spec.md`
4. 创建并归档 `catalog-block-read-watchlist-review-and-export-bundle` change lifecycle。

## Open Questions

- 无。V1 只 formalize 最小增量 bundle、统一 `--block-code` fanout 和 preset-owned export 参数边界。
