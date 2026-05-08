## Context

截至 `2026-05-02`，仓库已经具备两层 replay 基础设施：

- built-in provider replay fixture bundle
- in-process replay provider mode

同时，正式 CLI 入口已经在代码上暴露了 `--provider-mode replay`、`--fixture`、`--fixture-path` 等接缝，并且 `subscription-watch` 可以在 replay mode 下物化 completed run artifacts。问题不在于“能不能本地跑通”，而在于这些行为还没有被固化成稳定的子进程级 transport contract。

当前上层项目如果通过 `tdxquant ... --provider-mode replay` 做离线联调，仍然会遇到这些不稳定点：

- nested `api` 虽然普遍接受 replay 参数，但并不是所有命令都有 fixture backing
- flat replay 命令的支持矩阵与失败语义没有被正式锁定
- `stdout` 与 `--output` 的关系还没有被明确定义为 transport contract
- `subscription-watch` replay source 损坏时，调用方需要依赖底层异常文本而不是稳定 failure result

因此，这次设计不是扩新能力，而是把现有 replay 能力提升成正式的 CLI subprocess contract。

## Goals / Non-Goals

**Goals:**

- 固化支持 replay 的正式 CLI 命令矩阵。
- 固化 `--provider-mode replay`、`--fixture`、`--fixture-path`、`--output` 的选择算法和冲突规则。
- 固化 replay success / failure 在 `stdout`、`stderr`、exit code 上的 transport 语义。
- 固化 `task subscription-watch --provider-mode replay` 的 artifact 发现字段、legacy alias 字段和 malformed replay bundle 失败语义。
- 确保 replay mode 下不存在 silent fallback 到 live Windows runtime。

**Non-Goals:**

- 不新增 HTTP replay 服务。
- 不新增 replay wrapper 命令。
- 不扩大 live runtime capability 覆盖范围。
- 不重新设计 manager 级 replay 分发逻辑。
- 不把所有 CLI 命令都提升为 replay-supported。

## Decisions

### 1. 继续复用正式 CLI 入口，不新增 replay wrapper 命令

保留：

- `tdxquant api ... --provider-mode replay`
- flat replay provider commands
- `tdxquant task subscription-watch --provider-mode replay`

不新增 `transport-replay` 之类的包装命令。

原因：

- 上层项目联调的就是正式入口本身，而不是一套只用于 replay 的二次协议。
- 可以直接锁定真实入口的 `stdout`/exit code/JSON contract。

### 2. 在 CLI 层集中实现 replay policy

CLI 顶层负责：

- nested `api` replay 支持矩阵
- flat replay 支持矩阵
- selector algorithm
- replay failure normalization
- `stdout` / `--output` 一致性

底层 replay helper 只负责 fixture resolution 和 `subscription-watch` materialization。

原因：

- transport contract 天然属于入口层，而不是 manager 或 helper 层。
- 如果把 replay 规则分散在每个命令分支里，后续 capability 一多就会漂。

备选方案是命令级散点补强，但那会让失败语义和支持矩阵难以统一。

### 3. replay selector 采用固定算法，而不是“优先级文案”

规则固定为：

1. `--fixture-path`
2. `--fixture`
3. capability default fixture

同时 `--fixture` 与 `--fixture-path` 必须互斥。

原因：

- 上层调用方需要的是可编码的规则，不是口头上的“哪个优先”。
- 互斥先于选择，能避免“给了两个参数但 CLI 悄悄选一个”的歧义。

### 4. replay failure 必须返回稳定 JSON，而不是把 traceback 当 contract

所有 replay transport failure 统一表现为：

- 非零 exit code
- `stdout` 仍然是单个 JSON failure result
- `data.replay_source` 总是存在，至少包含 `mode=replay` 和 capability

原因：

- 上层项目需要稳定 parse `stdout`，不应依赖 stderr 或 traceback 文本分支。
- 这也是 no-live-fallback 的最直接证明：调用方可以从 failure payload 中看到 replay source。

### 5. `subscription-watch` replay 只物化 completed run，不模拟实时会话

`task subscription-watch --provider-mode replay` 的语义固定为：

- 立即物化新的 run artifact 目录
- 返回 completed task result
- 不模拟延时、轮询、心跳、逐条推送

原因：

- 当前目标是 subprocess contract hardening，不是 transport emulator。
- completed-run materialization 足够支撑离线 contract test 和 artifact 消费方联调。

备选是模拟实时回放，但那会把本次迭代推向 event scheduler / daemon 方向，范围过大。

## Risks / Trade-offs

- **[Risk] nested `api` 表面上对更多命令暴露 replay 参数，但只有一部分正式支持。**
  - Mitigation: 在 CLI 层显式拒绝 unsupported replay command，并返回稳定 failure result。

- **[Risk] 当前提交同时落了 replay mode 基础实现和 CLI transport hardening，边界容易混淆。**
  - Mitigation: 本 change 只对 CLI contract 变化建模，不重复声明 manager-level replay 基础设施。

- **[Risk] `subscription-watch` replay source 的显式路径可能包含结构上合法但语义不完整的资产。**
  - Mitigation: materializer 做完整性校验，缺失必要文件或 bundle 结构不匹配时稳定失败。

- **[Trade-off] 不做 wrapper 命令意味着 CLI 顶层逻辑会继续承担更多 replay policy。**
  - Mitigation: 规则集中在少数 helper 中，而不是散落在命令处理分支。
