# Catalog Block Read Watchlist Review And Export Bundle Design

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
- pure read bundle
  - `read-zxg-review`（已落地，是这条三步 bundle 的直接先例）

因此，这一包的真实缺口不是新增底层能力，而是把现有三条稳定入口收成一条更高层、仍然无复杂参数模型的 catalog bundle：

1. 先读取标准化 watchlist snapshot
2. 再看完整 diagnostics
3. 最后把 snapshot 导出到既有 preset 固定路径

## Goals

- 新增一条稳定 bundle：`read-zxg-review-and-export`
- 固定三步顺序：
  1. `read-zxg-watchlist`
  2. `read-zxg-full`
  3. `export-zxg-watchlist`
- 继续复用现有 bundle schema、step 解析和 dispatch 逻辑
- 允许顶层 `--block-code` 统一覆盖三步的默认值
- 保持 export step 的 `export_output` 继续来自 preset 默认值
- 验证现有：
  - `catalog list --kind bundle`
  - `catalog list --bundle ...`
  - `catalog plan --bundle ...`
  - `catalog run --bundle ...`
  对该 bundle 的端到端可用性

## Non-Goals

- 不新增 bundle schema
- 不新增新的 provider capability
- 不新增新的 task command
- 不做 inline 每步参数输入
- 不做顶层 `--export-output` 覆盖
- 不做 report
- 不做写回上层系统
- 不做后台服务或分布式执行
- 不做多 block 批量读取

## Decision 1: Reuse the existing bundle schema exactly

V1 明确选择继续复用现有 `command-bundles.json` schema。

现有 bundle 结构已经稳定：

- `description`
- `labels`
- `steps`
  - `name`
  - `entry`
  - 可选 `options`

因此，`read-zxg-review-and-export` 必须继续写成普通 bundle，而不是引入新的：

- `kind`
- `shared_args`
- `global_defaults`
- `step_groups`
- `export_defaults`

### Example bundle

```json
{
  "read-zxg-review-and-export": {
    "description": "先读取 ZXG 标准化快照，再查看完整诊断视图，最后导出 watchlist JSON。",
    "labels": ["block", "watchlist", "read", "review", "export"],
    "steps": [
      {
        "name": "snapshot",
        "entry": "read-zxg-watchlist"
      },
      {
        "name": "full",
        "entry": "read-zxg-full"
      },
      {
        "name": "export",
        "entry": "export-zxg-watchlist"
      }
    ]
  }
}
```

## Decision 2: The bundle remains a thin orchestration layer

`read-zxg-review-and-export` 的职责只有编排现有三条稳定入口。

它不是：

- 新的 provider capability
- 新的 task result schema
- 新的 export pipeline
- 新的 write-back workflow

因此：

- bundle 不新增自己的结果模型
- `export_output` 不在 bundle 层重复定义
- 所有 step 仍然走现有 preset-backed catalog entry dispatch

## Decision 3: `--block-code` is the only bundle-level override in V1

V1 明确允许：

- `catalog plan --bundle read-zxg-review-and-export --block-code MYZXG`
- `catalog run --bundle read-zxg-review-and-export --block-code MYZXG`

并要求该覆盖统一作用于三步：

- step 1 `read-zxg-watchlist`
  - `block_code = MYZXG`
- step 2 `read-zxg-full`
  - `block_code = MYZXG`
- step 3 `export-zxg-watchlist`
  - `block_code = MYZXG`

如果未显式给 `--block-code`，则三步继续使用各自 preset 的默认值：

- `ZXG`

这条规则有两个目的：

- 保持 bundle 只是编排既有 entry
- 避免在 V1 里引入每步单独参数建模

## Decision 4: `export_output` stays preset-owned in V1

V1 明确不支持：

- `catalog plan --bundle ... --export-output ...`
- `catalog run --bundle ... --export-output ...`

第三步 export 使用的输出路径继续完全来自：

- `export-zxg-watchlist` preset

原因是：

- `export_output` 当前属于有文件副作用的 task preset 默认值
- `overwrite: false` 也继续由 `export-zxg-watchlist` preset 持有
- 如果现在把它提升到 bundle 顶层，会立刻引入：
  - 路径覆盖语义
  - 三步中只有一步消费该参数的特殊规则
  - plan/run 展示面复杂化

V1 不承担这层复杂度。

## Decision 5: Failure semantics stay identical to existing bundles

V1 不为 `read-zxg-review-and-export` 发明新的失败语义。

继续复用现有 bundle 规则：

- step 1 失败
  - bundle 立即停止
  - 不执行 step 2 / step 3
- step 2 失败
  - bundle 立即停止
  - 不执行 step 3
- step 3 失败
  - bundle 返回失败
- 不新增 bundle 专属错误模型
- 不做回滚

这条语义特别适合当前场景，因为：

- step 1 / step 2 是纯读
- step 3 才有文件副作用
- 因此前两步失败时不存在需要清理的外部副作用

## Decision 6: V1 formalizes list, plan, and run on the existing bundle path

V1 只承诺这几条现有路径可用：

- `catalog list --kind bundle`
- `catalog list --bundle read-zxg-review-and-export`
- `catalog plan --bundle read-zxg-review-and-export`
- `catalog run --bundle read-zxg-review-and-export`

并继续复用现有：

- `--from-step`
- `--to-step`
- `--only-step`

这条 change 本身不需要为 `read-zxg-review-and-export` 设计新的 step-selection 语义。

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
  - bundle 停止，返回失败
- step 3 export task failure
  - bundle 返回失败
- 如果 `export-zxg-watchlist` preset 指向的 JSON 文件已存在
  - step 3 也会因为 `overwrite: false` 返回失败
  - 这属于既有 export task 语义，不在 bundle 层另做特殊处理

这条线不新增新的 bundle error schema。

## Implementation surface

V1 的必需改动只有这些：

- `runtime/command-bundles.json`
  - 新增 `read-zxg-review-and-export`
- `tests/test_api_cli.py`
  - 补 bundle list / plan / run focused coverage
- `runtime/TdxQuant_Task_Layer_Usage.md`
- `docs/TdxQuant_Project_Function_Map.md`
- `docs/TdxQuant_Next_Steps.md`
- `openspec/specs/tdx-command-catalog/spec.md`

原则上不应该需要修改：

- `tdxquant/catalog.py`
- `tdxquant/cli.py`
- provider contracts
- task logic
- preset schema
- catalog entry schema

唯一例外是：

- 当前 `tdxquant/cli.py` 已经因为 `read-zxg-review` 落地了 bundle-level `--block-code`
  - 所以这条 change 不应再重复修改 catalog parser
- 如果 focused tests 暴露现有 bundle runner 对三步 fanout 或 step short-circuit 存在缺口
- 才最小化修补相应 runtime 逻辑

## Test boundaries

第一版 focused tests 只覆盖这条增量：

- 默认 `catalog list --kind bundle` 能看到 `read-zxg-review-and-export`
- `catalog list --bundle read-zxg-review-and-export`
  - 返回正确的 step metadata
- `catalog plan --bundle read-zxg-review-and-export`
  - `selected_step_count == 3`
  - step 1 解析到 `read-zxg-watchlist`
  - step 2 解析到 `read-zxg-full`
  - step 3 解析到 `export-zxg-watchlist`
- `catalog plan --bundle read-zxg-review-and-export --block-code MYZXG`
  - 三步都解析成 `MYZXG`
  - step 3 仍展示 preset 自带的 `export_output`
- `catalog run --bundle read-zxg-review-and-export`
  - 继续走现有 bundle dispatch
- `catalog run --bundle read-zxg-review-and-export --block-code MYZXG`
  - 三步都收到 `MYZXG`
- step 2 失败时
  - bundle 停止
  - 不执行 step 3

## Migration plan

1. 在 `runtime/command-bundles.json` 新增 `read-zxg-review-and-export`
2. 在 `tests/test_api_cli.py` 增加 focused bundle list / plan / run coverage
3. 如果测试需要，再最小补 runtime 逻辑缺口
4. 同步文档与主 spec：
   - `runtime/TdxQuant_Task_Layer_Usage.md`
   - `docs/TdxQuant_Project_Function_Map.md`
   - `docs/TdxQuant_Next_Steps.md`
   - `openspec/specs/tdx-command-catalog/spec.md`
5. 通过 review 后，进入 implementation plan
