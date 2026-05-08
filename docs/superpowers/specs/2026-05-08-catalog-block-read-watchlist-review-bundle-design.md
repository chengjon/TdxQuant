# Catalog Block Read Watchlist Review Bundle Design

## Context

当前 `block` 读侧已经具备稳定层级：

- provider capability
  - `block.read_watchlist_snapshot(...)`
- task entries
  - `task block-read-watchlist`
  - `task block-read-full`
  - `task block-read-watchlist-export`
- task presets
  - `task run --preset read-zxg-watchlist`
  - `task run --preset read-zxg-full`
  - `task run --preset export-zxg-watchlist`
- catalog entries
  - `read-zxg-watchlist`
  - `read-zxg-full`
  - `export-zxg-watchlist`

同时，catalog bundle 基础设施已经存在并可工作：

- bundle registry 文件：
  - `runtime/command-bundles.json`
- bundle resolver / dispatcher：
  - `resolve_command_bundle(...)`
  - 既有 `catalog plan --bundle ...`
  - 既有 `catalog run --bundle ...`
- 现有 bundle 已支持：
  - step 顺序执行
  - `--from-step / --to-step / --only-step`
  - 顶层 CLI 参数统一下传到各 step
  - 任一步失败即停止后续 step

因此，这一包的真实缺口不是“新建一套 block read workflow 模型”，而是：

- 为 `block` 读侧新增一条 **纯读、无副作用** 的 preset-backed catalog bundle
- 让现有 bundle 机制把：
  - `read-zxg-watchlist`
  - `read-zxg-full`
  编排成一个稳定的日常入口

## Goals

- 新增一条稳定 bundle：`read-zxg-review`
- 让 bundle 先执行：
  1. `read-zxg-watchlist`
  2. `read-zxg-full`
- 继续复用现有 bundle schema、step 解析和 dispatch 逻辑
- 允许顶层 `--block-code` 统一覆盖两步的默认值
- 验证现有：
  - `catalog list --kind bundle`
  - `catalog list --bundle`
  - `catalog plan --bundle`
  - `catalog run --bundle`
  对该 bundle 的端到端可用性

## Non-Goals

- 不新增 bundle schema
- 不新增新的 provider capability
- 不新增新的 task command
- 不做 inline 每步参数输入
- 不做导出
- 不做 report
- 不做写回上层系统
- 不做后台服务或分布式执行
- 不做多 block 批量读取

## Decision 1: Reuse the existing bundle schema exactly

V1 明确选择**复用现有 `command-bundles.json` schema**。

现有 bundle 结构已经稳定：

- `description`
- `labels`
- `steps`
  - `name`
  - `entry`
  - 可选 `options`

因此，`read-zxg-review` 必须继续写成普通 bundle，而不是引入新的：

- `kind`
- `entry_type`
- `global_defaults`
- `shared_args`
- `step_groups`

之类字段。

### Example bundle

```json
{
  "read-zxg-review": {
    "description": "先读取 ZXG 标准化快照，再查看完整诊断视图。",
    "labels": ["block", "watchlist", "read", "review"],
    "steps": [
      {
        "name": "snapshot",
        "entry": "read-zxg-watchlist"
      },
      {
        "name": "full",
        "entry": "read-zxg-full"
      }
    ]
  }
}
```

## Decision 2: The bundle remains a pure read-side orchestration

`read-zxg-review` 的职责只有：

1. 看标准化 snapshot
2. 再看完整 diagnostics

它不是：

- report pipeline
- export pipeline
- write-back pipeline

因此：

- bundle 不包含 `export-zxg-watchlist`
- bundle 不包含任何文件输出参数
- bundle 不新增自己的结果 schema
- bundle 继续直接返回现有 step 结果的组合视图

## Decision 3: `--block-code` is a bundle-level override applied to both steps

V1 明确允许：

- `catalog plan --bundle read-zxg-review --block-code MYZXG`
- `catalog run --bundle read-zxg-review --block-code MYZXG`

并且要求该覆盖统一作用于两步：

- step 1 `read-zxg-watchlist`
  - `block_code = MYZXG`
- step 2 `read-zxg-full`
  - `block_code = MYZXG`

如果未显式给 `--block-code`，则两步继续使用各自 preset 的默认值：

- `ZXG`

这条规则有两个目的：

- 避免为 bundle 引入每步单独参数建模
- 保持“bundle 只是编排既有 entry”的定位

这一点在实现上有一个**明确前提**：

- `catalog plan --bundle ...` / `catalog run --bundle ...` 当前 parser 必须补 `--block-code`
- 也就是需要在 `tdxquant/cli.py` 的 `_add_catalog_run_arguments(...)` 中显式注册：
  - `subparser.add_argument("--block-code")`

否则：

- argparse 会在 dispatch 前直接拒绝 `--block-code`
- Decision 3 的覆盖语义就无法成立

## Decision 4: Failure semantics stay identical to existing bundles

V1 不为 `read-zxg-review` 发明新的失败语义。

继续复用现有 bundle 规则：

- step 1 失败
  - bundle 立即停止
  - 不执行 step 2
- step 2 失败
  - bundle 返回失败
- 不新增 bundle 专属错误模型
- 不把 provider/task failure 重新翻译成另一套 read-review failure

也就是说：

- 这条 bundle 是 orchestration
- 不是新的业务语义层

## Decision 5: V1 only formalizes list, plan, and run on the existing bundle path

V1 只承诺这几条现有路径可用：

- `catalog list --kind bundle`
- `catalog list --bundle read-zxg-review`
- `catalog plan --bundle read-zxg-review`
- `catalog run --bundle read-zxg-review`

并继续复用现有：

- `--from-step`
- `--to-step`
- `--only-step`

但这条 change 本身不需要为 `read-zxg-review` 设计新的 step-selection 语义。

## Error semantics

V1 的错误语义继续复用现有 catalog bundle 逻辑：

- bundle 不存在
  - 稳定失败
- bundle step 引用不存在的 entry
  - 稳定失败
- `--from-step / --to-step / --only-step` 非法
  - 稳定失败
- step 1 task failure
  - bundle 停止，返回失败
- step 2 task failure
  - bundle 返回失败

这条线不新增新的 bundle error schema。

## Implementation surface

V1 的**必需改动**只有这些：

- `runtime/command-bundles.json`
  - 新增 `read-zxg-review`
- `tdxquant/cli.py`
  - 在 `_add_catalog_run_arguments(...)` 中新增 `--block-code`
- `tests/test_api_cli.py`
  - 补 bundle list / plan / run focused coverage

只有在测试再暴露额外缺口时，才最小改动：

- `tdxquant/catalog.py`

原则上**不应该需要修改**：

- provider contract
- `block-read-watchlist` task logic
- `block-read-full` task logic
- preset schema
- catalog entry schema

## Test boundaries

第一版 focused tests 只覆盖这条增量：

- 默认 `catalog list --kind bundle` 能看到 `read-zxg-review`
- `catalog list --bundle read-zxg-review`
  - 返回正确的 step metadata
- `catalog plan --bundle read-zxg-review`
  - `selected_step_count == 2`
  - step 1 解析到 `read-zxg-watchlist`
  - step 2 解析到 `read-zxg-full`
  - 默认 `block_code == ZXG`
- `catalog plan --bundle read-zxg-review --block-code MYZXG`
  - 两步都解析成 `MYZXG`
- `catalog run --bundle read-zxg-review`
  - 继续走现有 bundle dispatch
- `catalog run --bundle read-zxg-review --block-code MYZXG`
  - 两步都收到 `MYZXG`
- step 1 失败时
  - bundle 停止
  - step 2 不执行

不要求：

- 新 replay fixture
- 新 report 测试
- 新 export 测试
- 多 block 组合测试

## Migration plan

1. 在 `runtime/command-bundles.json` 新增 `read-zxg-review`
2. 用 focused CLI tests 锁住 bundle list / plan / run
3. 只在必要时修正 bundle dispatch 的最小缺口
4. 同步更新这些现有文档：
   - `runtime/TdxQuant_Task_Layer_Usage.md`
   - `docs/TdxQuant_Project_Function_Map.md`
   - `docs/TdxQuant_Next_Steps.md`
   - `openspec/specs/tdx-command-catalog/spec.md`
5. 再补这条 bundle 的 OpenSpec lifecycle：
   - `openspec/changes/<change>/proposal.md`
   - `openspec/changes/<change>/design.md`
   - `openspec/changes/<change>/tasks.md`
   - `openspec/changes/<change>/specs/tdx-command-catalog/spec.md`

## Open questions

- 无。V1 只 formalize 一个纯读、两步顺序、顶层 `--block-code` 统一覆盖的最小 bundle。
