## Context

TdxQuant 已经有 provider-facing discovery 三件套：`runtime.capabilities`、`runtime.health`、`runtime.doctor`。上一轮已经把同步 provider envelope 收紧到统一外壳，但 discovery payload 内核仍然有两个问题：

- 一部分高价值字段虽然已经出现在实现里，但还没有被正式锁成 contract，例如 capability summary、grading 字典、probe context；
- 一部分诊断建议仍然偏向人类可读字符串，例如 `recommended_actions`，缺少稳定的 machine-readable action identity，导致上层难以直接做自动分流或 UI 映射。

这轮不新增命令，不扩 transport，也不做 fake provider mode；只把现有 discovery payload 收成稳定契约，并用 fixtures + tests 锁住。

## Goals / Non-Goals

**Goals:**

- 固定 `runtime.capabilities` 的 registry row、summary、grading 结构。
- 固定 `runtime.health` 的 `context / checks / warnings / recommended_actions` 语义。
- 为 health/doctor 引入结构化 `recommended_action_items`，同时保留现有字符串列表兼容。
- 固定 `runtime.doctor` finding 的 machine-readable `id`、severity、status 和 action linkage 规则。
- 把 discovery fixtures 升级成 contract snapshot，并补 manager/CLI/fixture 测试。

**Non-Goals:**

- 不新增 `runtime.preflight`。
- 不引入 HTTP discovery service。
- 不做 fake provider mode 或 daemon replay。
- 不改同步 provider envelope 顶层字段。
- 不触碰 `subscription-watch`、trade、task、report、catalog` 的输出协议。

## Decisions

### Decision: Keep existing discovery commands and harden payloads in place

这轮不新开任何 discovery 命令，只升级现有 `capabilities / health / doctor` 的 `data` payload。

Rationale:

- 路线图当前缺的是“可依赖的 discovery contract”，不是“更多入口”。
- 保持命令不变可以让改动集中在 payload 归一化和测试，而不是入口迁移。

Alternatives considered:

- 新增 `runtime.preflight`：有价值，但会把 scope 从 hardening 扩成 capability expansion。
- 新增 HTTP discovery：超出当前阶段。

### Decision: Add structured `recommended_action_items` while preserving legacy `recommended_actions`

`recommended_actions` 继续保留为字符串数组兼容字段；同时新增 `recommended_action_items` 作为 machine-readable 结构，每项至少包含 `id`、`summary`、`severity`、`related_checks`。

Rationale:

- 直接把字符串列表改成对象数组会制造 payload breaking。
- 双轨一段时间能让上层先消费结构化字段，再逐步淡化旧字符串列表。

Alternatives considered:

- 立即把 `recommended_actions` 改成对象数组：更干净，但风险更高。
- 继续只保留字符串列表：无法解决当前 machine-readable action identity 的缺口。

### Decision: Reuse check names as stable finding/action anchors where possible

对 check-driven 诊断，继续使用稳定 check 名作为 finding 和 action 的主锚点。例如 `query_runtime`、`desktop_window`、`hid`。健康全绿场景保留专用稳定 finding id，例如 `provider-ready`。

Rationale:

- 当前 check 名已经是最稳定的 machine-readable domain language。
- 重造一套完全独立的 ID registry 没有必要，只会增加维护负担。

Alternatives considered:

- 引入新的 opaque UUID 风格 ID：对上层没有可读价值，还增加 mapping 成本。
- 继续允许自由文本 finding id：不适合 contract。

### Decision: Treat bundled discovery fixtures as authoritative contract snapshots

`runtime-capabilities-success`、`runtime-health-degraded`、`runtime-doctor-degraded` 这类 fixture 视为 discovery contract snapshot，而不是松散样例。

Rationale:

- discovery 是上层在“调用前”最先消费的 payload，没有 snapshot 测试很容易漂。
- fixtures 能同时服务 manager、CLI、跨语言集成和后续 fake provider 设计。

Alternatives considered:

- 只补文档不补 fixtures：文档和实际 payload 容易再分裂。
- 直接上 fake provider mode：价值更高，但明显超 scope。

## Risks / Trade-offs

- [兼容字段变多] → 通过明确 `recommended_actions` 是兼容字符串投影、`recommended_action_items` 才是新 canonical 结构，避免长期双轨失控。
- [新增结构化 action 字段会牵动 fixtures 和测试] → 这是刻意选择；让差异在仓内暴露，而不是留给上层联调。
- [现有健康/诊断实现偏 check-driven，表达力有限] → 本轮接受这个边界，只要求稳定字段和稳定 ID，不追求更复杂的诊断图模型。
- [只硬化 payload，不扩新命令] → 这是有意为之；先把现有 contract 做实，再考虑 `preflight` 或 HTTP service。

## Migration Plan

1. 更新 OpenSpec requirement，明确 discovery payload 的稳定字段和兼容策略。
2. 调整 `provider_discovery.py` 与 `api/bridge.py`，补结构化 `recommended_action_items` 和稳定 finding/action linkage。
3. 更新 discovery fixtures、fixture registry 和 contract tests。
4. 更新 discovery 文档，明确 canonical payload 与兼容字段。
5. 后续如需移除兼容字符串列表，再单独开 change。

## Open Questions

- None for this change. The scope is intentionally limited to payload hardening for existing discovery commands.
