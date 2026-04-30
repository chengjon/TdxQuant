## Context

TdxQuant 现在已经具备较完整的 query/formula/block/runtime manager 与 CLI 主线，也已经为同步结果固定了 canonical provider result envelope。但两个上层项目的反馈都说明，只有结果协议还不够，调用方还需要在真正发起请求前回答几个问题：

- 当前 provider 暴露了哪些 capability
- 每个 capability 的稳定性与副作用级别是什么
- 当前平台、TongDaXin runtime、subscription runtime、窗口探测和 HID 链路是否可用
- 如果环境不健康，调用方应该先修什么

当前工程里已经有可以复用的基础：

- `run_tdx_bridge_health(...)` 可以提供 TongDaXin runtime、桌面窗口和 HID 的一部分探测
- `TdxApiManager.runtime.open_subscription_session()` 已经把 subscription session 做成独立能力
- provider-facing result envelope 已经落地，manager/CLI 都能输出稳定的同步 JSON 包络

但这些能力还没有被整理成正式的 provider discovery contract。现在的约束也比较明确：

- 不能把 capability registry 下沉到每个业务域模块里逐个自管
- 不能把 `task / report / catalog` 作为 discovery contract 的正式一部分
- 不能让 discovery 命令只返回自由文本，否则无法支持 bridge/contract test
- 不能把“环境不健康”直接等同于“探测命令执行失败”，否则上层难以稳定消费完整诊断结果

## Goals / Non-Goals

**Goals:**

- 定义 provider-facing capability registry 的第一版稳定字段
- 为 discovery/health/doctor 建立统一的同步 JSON contract
- 通过 `TdxApiManager.runtime` 与 CLI 提供正式入口
- 固定 capability 稳定性分级与副作用分级的基础字面值
- 固定 runtime health checks 与 doctor findings 的结构化表示
- 复用已有 provider result envelope，而不是再发明一套 discovery 顶层结构

**Non-Goals:**

- 不引入 HTTP 服务或 daemon 控制面
- 不定义 subscription JSONL 流协议
- 不把 `task / report / catalog` 包进 discovery mainline
- 不为 desktop trade 建立正式 provider capability contract
- 不在本包中定义 `formula.screen` 的最终 payload schema

## Decisions

### 1. 使用独立 provider capability registry，而不是让业务域各自散落声明

本包将引入一份共享 capability registry，在 provider boundary 集中声明 capability metadata，例如：

- canonical capability name
- capability version
- domain/category
- stability grade
- side-effect grade
- supported entrypoints
- runtime dependency hints

理由：

- 上层系统关心的是 provider 暴露面，而不是 Python 内部模块分布
- 集中 registry 更适合后续生成 discovery 响应、fixtures 与 contract tests
- 避免每个业务域重复维护格式不一致的元数据

备选方案：

- 让每个 domain manager/bridge 方法自带 discovery metadata  
  否决原因：横切字段会散落在多个模块中，后续难以统一校验和导出。

### 2. `capabilities` 返回静态暴露面与 grading，`health` 返回实时探测，`doctor` 返回行动建议

这三个入口分工明确：

- `capabilities`: 主要回答“理论上暴露了哪些能力，以及它们的稳定性/副作用级别是什么”
- `health`: 主要回答“当前运行环境和关键 runtime 是否可用”
- `doctor`: 在 `health` 基础上输出结构化 findings、严重度和推荐动作

`capabilities` 不依赖实时 runtime 探测结果来决定 capability 是否存在；实时 availability 由 `health` / `doctor` 表达。

理由：

- 将静态暴露面和动态健康状态分开，避免一个接口承担过多语义
- 上层系统可以先缓存 capability registry，再按需做 health probe
- 也更利于后续引入 HTTP 层和 replay/fake 模式

备选方案：

- 让 `capabilities` 同时承担实时探测和 registry 导出  
  否决原因：语义混杂，缓存与实时调用需求冲突。

### 3. 诊断类命令的成功语义表示“探测执行完成”，健康状态放进 `data`

对于 `health` 和 `doctor`：

- 若探测流程本身正常执行完成，则 top-level `success` 保持 `true`
- 当前环境是否健康，使用 `data.overall_status`、`checks`、`findings` 表达
- 只有探测逻辑本身异常无法产出结构化结果时，才返回 top-level failure

理由：

- 上层系统需要完整诊断负载，而不只是一个非零退出码
- 如果把环境不健康直接映射到 top-level failure，CLI 与 bridge 很难区分“诊断完成但环境坏”与“诊断自己崩了”

备选方案：

- 让任一 check 失败就令整个命令 top-level failure  
  否决原因：会损失结构化诊断信息，不利于自动修复与分流。

### 4. discovery 命令复用 provider result envelope，并扩展其适用范围

`capabilities`、`health`、`doctor` 都将直接复用已落地的 provider result envelope，不引入第二套 discovery 顶层 JSON。

理由：

- 上层系统已经明确希望 capability discovery 与普通同步调用共用 machine contract
- 这样 Rust/Python/HTTP bridge 后续都能复用同一套 envelope 解析器

备选方案：

- 单独设计 discovery-only 顶层结构  
  否决原因：会让 provider contract 分叉，增加客户端复杂度。

### 5. 继续保留低层 `tdx-bridge-health`，但正式 provider contract 使用新命令

现有 `tdx-bridge-health` 更像 bridge/debug 入口，字段形状和命名并不是围绕上层 provider 集成设计的。本包不会删除它，而是新增正式入口：

- `api capabilities`
- `api health`
- `api doctor`
- `tdx-capabilities`
- `tdx-health`
- `tdx-doctor`

理由：

- 保护现有调试路径，不破坏已有人工使用方式
- 正式 provider contract 可以从一开始就保持更清晰的 naming 和 schema

备选方案：

- 直接修改 `tdx-bridge-health` 成为正式 contract  
  否决原因：会把调试语义和 provider contract 语义耦在一起，兼容成本更高。

### 6. 采用固定 grading literals，优先覆盖稳定性和副作用两个维度

第一版 capability grading 先固定两组字面值：

- `stability`: `stable`, `beta`, `experimental`
- `side_effect_level`: `read_only`, `local_state_mutating`, `live_side_effecting`

理由：

- 两个上层项目都明确要求这两个维度
- 先把最基础、最有集成价值的 grading 做稳，比一次性引入更多维度更可控

备选方案：

- 现在就加入更多复杂维度，例如 transport maturity、broker specificity  
  否决原因：首包范围过大，可在后续迭代中增补。

## Risks / Trade-offs

- [Capability registry 需要持续维护] → 先显式集中维护，后续再评估是否要生成式同步；第一包优先保证清晰和稳定。
- [Health/doctor 可能误导为“全部命令都可自动执行”] → 在 capability metadata 中明确 stability 与 side-effect level，并将交易类能力继续排除在正式 provider mainline 之外。
- [诊断成功但环境不健康的语义容易被误解] → 用 spec、tests 和文档明确 `success` 表示“诊断已产出结构化结果”，真实健康结论看 `data.overall_status`。
- [桥接层探测逻辑重复] → 复用现有 `run_tdx_bridge_health` 的子逻辑，并抽出共享 probe helper，避免 manager/CLI/bridge 三处各自探测。
- [后续 HTTP provider 还要再包一层] → 让 capability registry 和 health payload 都保持 provider-neutral 命名，便于未来直接复用。

## Migration Plan

1. 建立 capability discovery 的 OpenSpec requirements。
2. 引入共享 registry 与 probe helper，并先补 bridge/manager/CLI 测试。
3. 在 runtime manager 与 CLI 暴露 discovery/health/doctor 正式入口。
4. 更新 provider result contract 文档，明确 discovery 已纳入同步 envelope 适用范围。
5. 后续再基于同一 registry 继续推进：
   - HTTP capabilities endpoint
   - replay/fake capability fixtures
   - `subscription-watch` 与 `formula.screen` contract

## Open Questions

- 第一版 capability registry 是否需要直接暴露 HTTP-friendly transport metadata，还是先保持 `manager` / `cli` 两类入口信息即可。
