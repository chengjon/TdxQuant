## Context

TdxQuant 已经完成第一版 provider-facing 同步结果 contract，并且把 query、formula、`runtime.capabilities`、`runtime.health`、`runtime.doctor` 纳入了统一 envelope 的大方向。但当前实现仍然存在 4 类不够硬的问题：

- manager 层、runtime discovery 和 CLI JSON 之间的字段齐备性不完全一致；
- 旧顶层 `ok` 与新顶层 `success` 仍处于过渡态，但兼容策略还没有被明确固定；
- CLI 失败时的退出码与 JSON 结构语义没有被同一份 contract 明确约束；
- replay fixtures 还是“代表样例”，还没有真正承担同步 provider contract snapshot 的角色。

当前项目路线图已经把“固定同步 JSON contract”和“capability discovery / health probe”列为高优先级主线，因此这轮变更不扩业务能力，而是把同步 provider contract 的公共外壳再硬化一版。

## Goals / Non-Goals

**Goals:**

- 让所有同步 provider 返回复用同一套 canonical envelope builder。
- 固定 `success` 为 canonical 布尔字段，同时保留 `ok` 作为一个版本周期的兼容别名。
- 固定 `runtime.capabilities`、`runtime.health`、`runtime.doctor` 与 query/formula 返回使用同一套顶层 envelope 规则。
- 固定 CLI JSON 输出与 Python manager 返回共享同一套 serializer 语义。
- 把 provider replay fixtures 升级成同步 provider contract 的稳定 snapshot 基线。

**Non-Goals:**

- 不引入 HTTP server 或新的 transport。
- 不调整 `subscription-watch` 或其他长时 JSONL event contract。
- 不统一 `task / report / catalog / desktop trade` 输出。
- 不重塑 capability-specific `data` payload，只收紧公共 envelope。
- 不在本轮移除 `ok` 兼容字段。

## Decisions

### Decision: Reuse a single canonical synchronous envelope builder

所有 manager-driven query、formula 和 runtime discovery 响应都继续通过同一个 provider envelope builder 输出，而不是为 discovery 或 CLI 单独维护变体。

Rationale:

- 这轮问题的核心不是能力不足，而是公共外壳在不同入口上仍然可能漂移。
- 把所有同步返回都收敛到一个 builder，可以把字段齐备性、默认容器类型、时间字段和兼容别名一次性固定下来。

Alternatives considered:

- 为 `capabilities / health / doctor` 保留单独 serializer：改动局部更小，但会继续留下 discovery 是“特殊返回”的分叉。
- 只在 CLI 侧补字段：会让 Python 和 fixtures 继续分裂，不能真正形成稳定 contract。

### Decision: Keep `ok` as a temporary top-level alias of `success`

`success` 继续作为 canonical 布尔字段；`ok` 保留一个版本周期并且必须与 `success` 完全一致。文档、fixtures 和新测试全部以 `success` 为主描述，同时显式记录 `ok` 的兼容期。

Rationale:

- 上层系统可能仍然依赖旧 `ok` 字段；直接移除会制造没有必要的 breaking change。
- 兼容优先可以让本轮聚焦在“结构收紧”，而不是“迫使所有消费者同步迁移”。

Alternatives considered:

- 立即移除 `ok`：协议更干净，但与当前兼容优先的策略冲突。
- 永久保留双字段：会把过渡态固化成永久状态，后续更难清理。

### Decision: CLI JSON keeps non-zero exit codes but MUST emit the same envelope

CLI 失败时仍然保持非零退出码，但只要命令进入 provider contract 路径，就必须输出与 Python 返回一致的 JSON envelope，而不是切换到自由文本或不完整 JSON。

Rationale:

- 上层脚本既需要 shell 级失败信号，也需要稳定 parse JSON 的能力。
- 退出码和 JSON 结构表达的是两个层面的语义，不应该互相替代。

Alternatives considered:

- CLI 失败时只输出文本错误：现有 shell 体验简单，但无法支持稳定 contract test。
- CLI 一律返回零退出码：方便 JSON-only 集成，但不符合现有命令行语义，也会弱化 shell 层的错误处理。

### Decision: Replay fixtures become contract snapshots for the hardened synchronous envelope

现有 provider replay fixtures 继续保留内置样例形式，但这轮开始要把同步 JSON fixtures 视为 contract snapshot，并新增针对 success/failure query-formula 和 runtime discovery 的覆盖。

Rationale:

- 只靠 live Windows runtime 很难持续验证 contract 不漂移。
- snapshot 化的 fixtures 能为未来 fake provider、transport replay、跨语言 contract test 提供稳定基线。

Alternatives considered:

- 只更新文档不更新 fixtures：文档会和实际样例分离，无法形成可执行 contract。
- 把 fixtures 直接升级成 fake provider mode：价值更大，但范围明显超出本轮 hardening。

## Risks / Trade-offs

- [兼容字段延长过渡期] → 通过在文档、fixtures 和测试里把 `success` 设为 canonical 字段，并把 `ok` 明确标成临时别名，避免双字段长期失控。
- [CLI 统一 serializer 可能影响现有错误路径] → 先只约束 provider contract 路径，不在本轮触碰 task/report/trade 等其他 CLI 域。
- [fixtures 变严会暴露更多历史不一致] → 这是预期结果；用 snapshot 测试把差异前移到开发阶段，而不是留给上层联调。
- [只硬化顶层 envelope，未重塑 `data` payload] → 这是刻意取舍。本轮先稳定跨能力通用外壳，避免 scope 膨胀。

## Migration Plan

1. 更新 OpenSpec requirement，明确 canonical envelope、兼容 alias、CLI 退出码与 discovery contract。
2. 调整 Python manager / provider discovery / CLI serializer 逻辑，使同步 provider 返回共用同一套顶层结构。
3. 更新 replay fixture 资产与对应测试，把 hardened envelope 作为 snapshot 基线。
4. 更新 provider result 与 discovery 文档，说明 `success` canonical、`ok` 兼容期和 CLI 语义。
5. 通过 manager、CLI、fixture 和 OpenSpec 校验后，再考虑后续是否单独开 change 移除 `ok`。

## Open Questions

- None for this change. The compatibility-first boundary, fixture scope, and discovery coverage have already been fixed for this round.
