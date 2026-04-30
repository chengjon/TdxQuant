## Context

TdxQuant 目前已经有较完整的查询、公式、manager 和 CLI 入口，但同步结果的 JSON 结构是沿实现路径自然生长出来的，还没有形成上层项目可依赖的稳定 provider contract。`mystocks` 与 `quantix-rust` 都已经明确要求：在继续接入 `formula`、`subscription`、`block` 之前，TdxQuant 必须先给出统一、可版本治理、可做 contract test 的机器协议。

这个变更是典型的 cross-cutting 变更：

- 它同时影响 manager 与 CLI 入口
- 它会改变现有 JSON shape，属于显式 breaking change
- 它必须为后续 capability discovery、subscription JSONL、replay/fake 夹具奠定统一边界

当前约束也很清楚：

- 不能把 provider contract 直接下沉到每个业务域，避免 domain 模块失去单一职责
- 不能把 `subscription`、`capability discovery`、`desktop trade` 一起打包，否则首包范围过大
- 不能把 `task / report / catalog` 入口层当成正式集成协议

## Goals / Non-Goals

**Goals:**

- 定义同步 provider-facing JSON result envelope
- 为 manager 驱动与 CLI JSON 输出建立同一套顶层 contract
- 固定 success/error、version、timing、runtime、artifacts 等公共字段语义
- 固定时间、symbol、枚举字面值与 CLI 退出码的基本规范
- 为后续 `formula.screen`、`subscription-watch`、capability discovery 提供统一边界

**Non-Goals:**

- 不定义 `subscription-watch` 的 JSONL 事件 contract
- 不定义 capability discovery / health probe 的响应 schema
- 不定义 `formula.screen` 的完整 `data` payload schema
- 不统一 `task / report / catalog` 的全部输出协议
- 不处理 desktop trade 输出协议与风险治理

## Decisions

### 1. 在 provider 边界统一同步 result envelope，而不是让业务域感知整套 contract

同步 provider contract 将在 manager 与 CLI 结果序列化边界统一生成，而不是让 `market`、`meta`、`formula`、`block`、`runtime`、`financial`、`transaction` 等业务域模块各自拼装完整 envelope。

理由：

- 业务域模块当前已经明确要求保持 profile-agnostic、业务语义单一
- provider contract 是横切 concern，更适合放在 manager/CLI 结果包装层
- 这样后续引入 capability discovery、subscription、replay 时，可以继续沿同一 provider boundary 演进

备选方案：

- 让每个 bridge/domain 方法直接返回最终 contract  
  否决原因：会把协议细节下沉到业务实现，放大跨域改动成本。

### 2. 先固定公共 envelope，再分阶段定义 capability-specific `data` schema

本包只固定公共 envelope，不试图一次性定义所有 capability 的 `data` 内容结构。

本包会稳定：

- `success`
- `code`
- `message`
- `capability`
- `capability_version`
- `schema_version`
- `request_id`
- `started_at`
- `finished_at`
- `elapsed_ms`
- `runtime`
- `warnings`
- `data`
- `artifacts`

其中 `data` 的 capability-specific 结构将在后续独立 change 中细化，例如 `formula.screen` schema。

理由：

- 上层项目当前最迫切的是稳定 envelope 与错误模型
- 如果把所有 payload schema 一次性并入，会显著扩大首包范围并拖慢落地

备选方案：

- 同时定义所有查询/公式 payload schema  
  否决原因：范围过大，且不同 capability 的成熟度不一致。

### 3. 统一 contract 需要显式版本字段，并接受这是 breaking change

所有同步 provider 输出都将显式携带：

- `capability`
- `capability_version`
- `schema_version`

现有 manager 返回结构与 CLI JSON shape 将向该 envelope 收敛，因此这是一项显式 breaking change。

理由：

- 上层项目需要长期兼容治理，而不是“隐式靠约定”
- 如果不在第一包就引入 version 字段，后续迁移成本会更高

备选方案：

- 先保持旧 shape，只加文档说明  
  否决原因：上层仍无法安全写 contract test，无法真正降低集成风险。

### 4. CLI 失败路径也必须输出机器可读结构，并与退出码形成双重 contract

当 CLI 处于 JSON-oriented 输出路径时：

- 成功时退出码必须为 `0`
- 失败时退出码必须为非 `0`
- 失败详情仍必须通过 JSON 输出表达，而不是只打印自由文本

理由：

- Rust/Python 上层都不能只靠 shell exit code 推断失败原因
- 上层项目既需要机器可读错误结构，也需要最基本的进程级成功/失败信号

备选方案：

- 失败时只返回非零退出码，正文自由输出  
  否决原因：不利于桥接服务和 contract test 自动解析。

### 5. 结果字段格式要在首包就固定基础规范

本包会同步固定以下基础格式规则：

- 时间字段使用 `RFC3339`
- symbol 使用字符串表达
- 枚举使用固定字面值，不使用自由文本
- `warnings` 与 `artifacts` 使用结构化集合，而不是拼接消息文本

理由：

- 这些格式问题一旦放到后续再统一，会直接造成跨语言模型迁移成本
- 这也是上层项目最容易在早期就依赖的部分

备选方案：

- 先只固定字段名，不固定格式  
  否决原因：会把真正的兼容性问题推迟到后面爆发。

## Risks / Trade-offs

- [Breaking JSON shape] → 在 proposal、spec、实现和发布说明中明确标记 breaking change，并优先补 contract fixture。
- [公共 envelope 与现有结果工具冲突] → 通过共享 result normalizer/helper 收口，避免多处手工拼装。
- [首包未覆盖 capability-specific payload schema，外部仍有剩余不确定性] → 在本包中明确 `data` 仅是稳定容器，后续优先推进 `formula.screen` contract。
- [CLI 与 manager 的语义边界被混淆] → 让公共 envelope 只承载公共字段，manager/profile 语义通过能力 spec 明确约束，不把入口层布局暴露成正式 contract。
- [未来 HTTP provider 再包一层时出现双重 envelope] → 当前设计把 contract 定义为 provider-facing canonical shape，后续 HTTP/bridge 层必须直接复用，而不是重新发明第二套顶层结构。

## Migration Plan

1. 先通过 OpenSpec 固定同步 result contract 的 requirement。
2. 在实现阶段引入共享 result normalizer/helper。
3. 先让 manager 驱动与 CLI JSON 输出统一到同一 envelope。
4. 为关键能力补最小 contract fixture，至少覆盖成功与失败路径。
5. 在后续独立变更中继续补：
   - `formula.screen` payload schema
   - capability discovery
   - `subscription-watch` JSONL contract

## Open Questions

- 本包不阻塞实现的前提下，`formula.screen` 的 capability naming 是否直接作为第一条样板 contract 推出，还是仅在后续 change 中正式固化。
