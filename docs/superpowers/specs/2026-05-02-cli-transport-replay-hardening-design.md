# CLI Transport Replay Hardening Design

## Context

截至 `2026-05-02`，项目已经具备两层 replay 基础设施：

- 包内稳定 provider replay fixture bundle
- in-process fake provider mode

当前正式入口已经能够在部分能力上执行：

- `TdxApiManager(..., provider_mode="replay")`
- `tdxquant api ... --provider-mode replay`
- `tdxquant task subscription-watch --provider-mode replay`

当前还已经存在两层可复用的 CLI replay 接缝：

- `_add_replay_provider_arguments(...)`
  - 统一注册 `--provider-mode`
  - 统一注册互斥的 `--fixture` / `--fixture-path`
- `_run_flat_replay_provider_command(...)`
  - 统一处理 flat replay 正式命令
  - 对不在 flat replay 范围内的命令返回稳定 `unsupported replay flat command`

同时，nested `api` 入口已经通过 `_add_api_common_arguments(...)` 为所有 `api` 子命令暴露 replay 参数，但这些子命令并不都拥有 replay fixture backing。

但这些能力还主要停留在“本地可跑”的层面，尚未被明确固化成 **CLI 子进程级 transport contract**。这意味着上层项目虽然可以通过调用 `tdxquant` 子进程完成离线联调，但仍缺少这些稳定约束：

- 哪些正式命令保证支持 replay
- `--fixture` / `--fixture-path` 的优先级和冲突语义
- `stdout`、`stderr`、exit code 的稳定边界
- `subscription-watch` replay materialization 的 artifact 发现方式
- replay 参数错误、fixture 缺失、fixture 非法时的统一失败语义

本设计将这条线收口为 **CLI transport replay hardening**，目标是让上层项目把 `tdxquant ... --provider-mode replay` 当成正式、可测试、可自动消费的离线 transport。

## Goals

- 把 CLI 子进程 replay 固化成正式 transport contract。
- 明确 replay 支持矩阵，只承诺正式 provider-facing 入口。
- 固定 `--provider-mode replay`、`--fixture`、`--fixture-path` 的加载与互斥规则。
- 固定 `stdout`、`stderr`、exit code 的 transport 语义。
- 固定 `subscription-watch` replay 的 artifact 发现与返回路径规则。
- 统一 replay 失败路径，确保不发生 silent fallback 到 live runtime。
- 为上层项目补齐 representative subprocess contract tests 与文档样例。

## Non-Goals

- 不引入 HTTP replay 服务。
- 不引入 SSE / stream transport。
- 不新增 `transport-replay` wrapper 命令。
- 不把所有 CLI 命令都提升为 replay-supported。
- 不扩大 live Windows runtime capability 覆盖范围。
- 不重做 `TdxApiManager` 的 replay 核心分发逻辑。
- 不改变 `TdxApiManager(..., replay_fixture_map=...)` 这类程序内 API 的语义；它属于 manager 级 programmatic selector，不是本次 CLI transport contract 的新增面。
- 不在本次设计中新增大规模 fixture 资产，只围绕现有 capability 与必要错误样例硬化。

## Approaches Considered

### Option A: Command-local hardening

在每个支持 replay 的命令分支里分别补 replay 参数校验、fixture 解析和错误兜底。

优点：

- 改动局部直观
- 进入实现最快

缺点：

- replay 规则会分散在多个命令分支
- stdout/stderr/exit code 语义容易漂移
- 后续扩 capability 时维护成本高

### Option B: Centralized CLI replay policy layer

在现有正式命令上保留 replay 入口，但把 replay 相关规则集中到一层统一 CLI policy：

- 支持矩阵
- 参数规则
- fixture 选择算法
- no-live-fallback
- transport-level output policy
- replay failure normalization

优点：

- 最符合“子进程 transport contract”目标
- replay 规则集中，便于测试和文档化
- 后续若升级到 HTTP transport，规则可迁移复用

缺点：

- 需要对 CLI 顶层分发做一定结构整理

### Option C: Centralized policy plus invocation manifest

在 Option B 基础上，再为每次 replay 调用输出显式 invocation manifest，记录 command、fixture、timing、artifacts、exit code 等。

优点：

- 调试与审计证据最完整

缺点：

- 超出当前范围
- 会把本次迭代从“transport hardening”推向“运行审计系统”

## Recommended Approach

采用 **Option B: Centralized CLI replay policy layer**。

原因：

- 当前用户已经明确本期只做 CLI 子进程级 replay，不做 HTTP。
- 目标不是“补几个 replay 参数”，而是形成稳定的子进程调用契约。
- 现有命令已经是正式入口；继续复用它们，能让上层直接联调真实入口而不是一个只给 replay 用的包装协议。
- 统一 CLI replay policy 能把参数规则、fixture 选择、transport 输出和异常兜底收在一处，避免 capability 越多越分裂。

## Supported Command Matrix

本次 change 只承诺以下两类正式入口支持稳定 CLI replay。

### Synchronous provider JSON commands

包括：

- 对应 flat bridge-oriented 正式命令，例如：
  - `tdx-capabilities`
  - `tdx-health`
  - `tdx-doctor`
  - `tdx-formula-screen`
  - `tdx-send-user-block`

以及 nested `api` 正式子命令中的以下子集：

- `tdxquant api capabilities --provider-mode replay`
- `tdxquant api health --provider-mode replay`
- `tdxquant api doctor --provider-mode replay`
- `tdxquant api formula-screen --provider-mode replay`
- `tdxquant api send-user-block --provider-mode replay`

原则：

- 只有已经具备稳定 replay fixture 和正式 provider contract 的 capability 才进入支持矩阵。
- 对于不在支持矩阵内的 flat 或 nested `api` 正式命令，开启 replay 必须稳定失败。
- nested `api` 入口虽然普遍注册了 replay 参数，但只有上述子命令进入正式 replay transport 支持矩阵；其他 `api` 子命令必须以稳定 failure 结束，而不是 silent fallback 到 live。
- `api send-user-block` 命令本身当前已经存在；本次 change 只硬化它的 replay transport contract，不新增这条 nested 命令。

### `task subscription-watch --provider-mode replay`

原则：

- replay mode 下不打开 live runtime subscription session
- 不模拟实时等待、延时或逐条推送
- 直接物化一份 completed-run artifact bundle，并返回稳定 task result JSON

### Out of scope commands

以下命令不进入本次 replay transport contract：

- 桌面交易命令
- 依赖真实 Windows runtime session 的低层实验命令
- 没有稳定 provider fixture 的非正式入口

## Replay Argument Policy

CLI replay 参数语义必须统一，不允许每个命令各自解释。

### Supported arguments

- `--provider-mode`
- `--fixture`
- `--fixture-path`
- `--output`

### Rules

1. `live` 仍是默认 provider mode。
2. `--provider-mode replay` 才会进入 replay transport policy。
3. `--fixture` 与 `--fixture-path` 必须互斥。
4. replay fixture 选择算法固定为：
   1. 若显式给出 `--fixture-path`，使用该外部路径
   2. 否则若显式给出 `--fixture`，使用该 built-in fixture name
   3. 否则使用 capability 默认 built-in fixture
5. 未命中 default fixture、显式 fixture 名称或显式 fixture 路径时，必须稳定失败。
6. replay mode 下严禁 silent fallback 到 live Windows runtime。
7. `--output` 在 replay mode 下仍然受支持；它写出的 JSON 必须与 stdout 主结果保持一致，而不是改变 transport contract。

## Subprocess Transport Contract

### stdout

`stdout` 是正式 machine-readable 主结果通道，不允许混入自由文本。

#### Synchronous provider JSON commands

- `stdout` 必须只输出一个 provider-facing JSON envelope
- 即使同时使用 `--output`，stdout 仍必须保留这个单一 JSON envelope；`--output` 只是额外文件镜像，不是 stdout 重定向

#### `task subscription-watch --provider-mode replay`

- `stdout` 必须只输出一个完成态 task result JSON
- 事件流不经由 stdout 输出
- 事件、状态、总结与 manifest 必须落到新物化的 run artifact 目录

### stderr

`stderr` 只用于人类可读诊断，不承载正式 contract。

规则：

- 成功时应为空，或仅保留极少量非契约提示
- 失败时可输出短诊断文本
- 机器消费必须始终以 `stdout` JSON 与 exit code 为准
- 不允许把正式 JSON 结果输出到 stderr

### exit code

exit code 表达 transport 调用是否成功，而详细失败原因由 `stdout` JSON 描述。

- `0`：replay transport 调用成功
- 非 `0`：replay transport 调用失败

失败场景至少包括：

- replay 参数错误
- fixture 缺失
- fixture 格式错误
- capability 不支持 replay
- replay materialization 失败

## Subscription Watch Replay Artifact Contract

`task subscription-watch --provider-mode replay` 的正式 transport contract 不只是“返回成功”，还必须稳定暴露 artifact 发现路径。

返回 JSON 必须显式包含：

- `run_id`
- `run_dir`
- `manifest_path`
- `status_path`
- `summary_path`
- `events_jsonl_path`
- `events_csv_path`

并保留现有兼容别名：

- `jsonl_output_path`
- `csv_output_path`
- `status_output_path`

规则：

- 这些路径必须指向 **本次新物化** 的 replay run 目录
- 不能原样复用源 fixture 路径
- artifact bundle 必须由 canonical run contract 组成：
  - `events.jsonl`
  - `status.json`
  - `summary.json`
  - `manifest.json`

## Replay Failure Normalization

这条线的关键不是“所有 replay 都成功”，而是所有失败都稳定、可消费、不可误判。

本次 change 需要统一收敛这些失败：

- 参数互斥冲突
- replay capability 不支持
- default fixture 缺失
- fixture 名称未命中
- fixture path 不存在
- fixture JSON / JSONL 内容非法
- `subscription-watch` replay bundle 缺文件或结构不完整

这些情况都应表现为：

- 非零 exit code
- `stdout` 仍输出稳定 failure JSON
- `stderr` 最多补简短诊断
- 不发生 traceback 级 contract 漂移
- 不访问 live runtime

failure JSON 应继续沿用现有 provider-facing envelope，并在失败路径中保留最小 replay metadata：

- `data.replay_source.mode = "replay"`
- `data.replay_source.capability = <requested capability>`

这样同步 JSON failure 结果与现有 `execute_sync_replay(...)` 约定保持一致。

## Implementation Surface

### `tdxquant/cli.py`

这是本次设计的主落点。

职责：

- 定义 replay 支持矩阵
- 执行 replay 参数互斥校验
- 统一 fixture 选择算法
- 统一 stdout / stderr / exit code 语义
- 统一 replay failure normalization

原则：

- transport policy 放在 CLI 顶层
- 不重复发明第二套 flat replay dispatch，而是在现有 `_run_flat_replay_provider_command(...)` 和 nested `api` 分发基础上做 contract hardening
- 不把 transport contract 逻辑散落到每个 capability 分支

### `tdxquant/replay_provider.py`

职责：

- capability 默认 fixture 解析
- built-in fixture 名称解析
- external fixture path 解析
- `subscription-watch` replay bundle materialization
- 明确区分“fixture 未命中”和“fixture 内容非法”

原则：

- `replay_provider.py` 负责 replay 解析与物化
- `cli.py` 负责 transport policy 与异常兜底

### `tdxquant/api/task.py`

只做必要的配合改动：

- 保证 `subscription-watch` replay task result 含完整 artifact 路径
- 保证 replay materialization failure 可被 CLI 稳定接住

本次不把 transport policy 下沉到 task 层。

## Testing Strategy

测试必须直接从“上层如何调用子进程”出发，而不只是锁内部 helper。

### 1. Support matrix tests

- 支持 replay 的正式命令能成功执行
- 不支持 replay 的正式命令稳定失败

### 2. Argument policy tests

- 同时给出 `--fixture` 与 `--fixture-path` 时，由 argparse 级互斥规则稳定拒绝
- 单独给出 `--fixture` 时，稳定命中指定 built-in fixture
- 单独给出 `--fixture-path` 时，稳定命中指定外部路径
- 未显式指定 fixture 时，默认 fixture 自动命中

### 3. Transport output contract tests

- 成功时 `stdout` 为单一 JSON
- 失败时 `stdout` 仍为单一 JSON failure
- `stderr` 不承载正式结果
- exit code 语义稳定
- replay mode 下同时使用 `--output` 时，stdout 仍输出单一 JSON envelope
- replay mode 下 `--output` 写入的文件内容与 stdout JSON 一致

### 4. Subscription watch replay artifact tests

- 返回值显式包含 `run_id`、`run_dir` 与核心 artifact 路径
- 这些路径指向新物化目录
- replay mode 不打开 live runtime subscription session

### 5. No-live-fallback tests

- capability 不支持 replay
- fixture 缺失
- fixture 内容非法

以上全部必须稳定失败，并通过下列至少一种方式证明不会访问 live runtime：

- 对 live bridge / runtime session 打桩并断言其未被调用
- 在无 Windows runtime 的环境里执行 replay 测试并确认成功或稳定失败
- 通过结构化测试证明 replay 代码路径只经过 fixture resolver / materializer，而不进入 live bridge 分发

## Risks

- 当前 CLI 文件仍较大，若不小心会把 transport policy 逻辑继续堆成新的分支泥团，因此需要保持 replay policy 边界明确。
- 不同正式命令当前的 JSON-oriented 输出路径可能存在历史差异，本次需要先统一而不是只补 happy path。
- `subscription-watch` replay 如果 artifact 重写不彻底，容易把 source fixture 路径泄漏给调用方，破坏“每次 materialize 新 run”的约束。
- nested `api` 子命令目前普遍接受 `--provider-mode replay` 参数，但多数子命令并没有 replay fixture backing；如果支持矩阵和失败契约不显式锁定，调用方会在运行时才发现边界。

## Acceptance Criteria

1. 正式支持矩阵中的 CLI 命令均可通过 `--provider-mode replay` 被上层项目稳定子进程调用。
2. `--fixture` / `--fixture-path` 规则统一，且不允许 silent fallback 到 live。
3. 成功与失败路径都满足稳定的 `stdout JSON + exit code` contract。
4. `stderr` 不承载正式 machine contract。
5. `task subscription-watch --provider-mode replay` 返回的新 run artifact 路径稳定且可直接消费。
6. 对应的 representative subprocess tests、fixture 使用文档和 OpenSpec 变更全部通过。
