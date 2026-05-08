# Block Sync Governance Hardening - Review

**Reviewer**: Claude Opus
**Date**: 2026-05-03
**Scope**: `openspec/changes/block-sync-governance-hardening/`
**Status**: Proposal + Spec 阶段，尚未实现

---

## 总评

这是一份设计质量较高的变更提案。在已有 `block_mutation` 写治理基础上新增 `block sync` capability 的思路清晰，职责分层合理（sync 负责同步语义，底层真实写入复用治理链）。Spec 覆盖面全面，8 个 design decisions 都有明确的取舍论证。

以下是按严重程度分类的具体意见。

---

## CRITICAL - 必须修复

### C1. Bridge 与 `apply_block_mutation_safety` 签名不兼容

`block_mutation.py:306-317` 的函数签名为 keyword-only（`*` 前缀），且要求 `observed_state` 和 `execute_write` 参数：

```python
def apply_block_mutation_safety(
    *,
    operation: str,
    block_code: str,
    execute_write: Callable[[], Result],
    observed_state: dict[str, Any] | Result | Callable[[], dict[str, Any] | Result],
    ...
)
```

但 `bridge.py:1019-1026` 的实际调用方式是：

```python
result = _run_tq_call(...)  # 先执行写操作
return apply_block_mutation_safety(
    result,                    # positional arg，但函数是 keyword-only
    operation="create_sector",
    block_code=block_code,
    ...
    # 缺少 observed_state
    # 缺少 execute_write
)
```

**问题**：
1. 传了 positional arg 给 keyword-only 函数 → runtime TypeError
2. 没传 `observed_state` → 治理决策无法读取真实状态，"写前治理"名存实亡
3. 没传 `execute_write` → 治理层无法控制是否执行底层写入

**建议**：tasks.md 应该把"升级 bridge 五条写路径为治理模式"作为独立显式 task，而不是隐含在 2.1 里。这是整个变更能工作的前提条件，当前 task 列表对这个关键步骤的描述太模糊。

### C2. 前置 change（block-write-governance-hardening）的实现未完成

对比 `archive/2026-05-01-block-write-governance-hardening/tasks.md`（全部标记 `[x]`）与实际 bridge 代码，bridge 并没有真正实现"写前读取真实状态"的治理模式。如果前置 change 的落地尚不完整，当前 change 的设计假设（"现有治理链已可用"）就不成立。

**建议**：在开始本 change 的实现之前，先验证前置 change 的实际落地状态。如果 bridge 尚未升级为治理模式，需要先完成那部分工作。

---

## HIGH - 强烈建议修复

### H1. `request_label` 在 design 和 spec 之间不一致

Design Decision 2 列出 `request_label` 作为 sync request contract 的输入字段，但 `tdx-provider-block-sync/spec.md` 的所有 scenario 中没有提及 `request_label`。如果确实需要这个字段，spec 应该补充 scenario；如果不需要，应从 design 中移除。

### H2. `show` 字段在 sync contract 中的处理未明确

`send_user_block` 的底层调用需要 `show` 参数，但 block sync 的 request contract（Design Decision 2）和 spec 都没有提到 `show`。需要明确：
- 如果 sync 不支持 `show`，spec 应声明默认行为（如 `show=true`）
- 如果 sync 支持 `show`，request contract 和 spec scenario 应包含它

### H3. Dry-run 的审计 artifact 行为在 spec 中不明确

Design Decision 5 明确说 dry_run "写审计 artifact"，但 `tdx-provider-block-sync/spec.md` 的 dry-run scenario 只说 "MUST NOT execute create-sector or send-user-block runtime writes"，没有说明 dry_run 是否也写 audit artifact。建议在 spec 中补充一个明确的 dry-run audit scenario。

### H4. Task 1.1 粒度过大

Task 1.1 "Add a dedicated block sync orchestration layer that normalizes symbols, computes observed/desired state, and supports replace and merge" 覆盖了至少三个独立关注点：
- sync orchestration 入口
- 状态规范化与 diff 计算
- replace / merge 模式切换

建议拆分为更小的原子 task，便于增量验证和 review。

---

## MEDIUM - 建议改进

### M1. `mutation_key` 在 sync 层与底层写层的语义冲突风险

Design Decision 7 和 Risk 4 都提到了 sync-level `mutation_key` 与底层 write-level `mutation_key` 可能冲突。当前设计说"sync capability 的 `mutation_key` 绑定的是 canonical sync request"。但当 sync 触发 `create_sector` + `send_user_block` 两步写时，底层治理链也会写各自的 audit artifact（带有各自的 mutation context）。

**建议**：明确说明底层写的 `mutation_key` 应该如何与 sync-level `mutation_key` 关联。选项包括：
- sync 不传 `mutation_key` 给底层（底层用自动生成的）
- sync 把自己的 `mutation_key` 传递给底层，但底层用独立的 idempotency 逻辑

### M2. `merge` 模式下 `noop` 的判定条件

`_decision_for_observed_state` 对 `send_user_block` 的判断是 `observed_stocks == desired_stocks`。在 `merge` 模式下，`desired_stocks = observed_stocks ∪ requested_symbols`。如果所有 `requested_symbols` 已经存在于 `observed_stocks` 中，结果就是 noop。这是正确的。

但 spec 只描述了 `replace` 场景的 noop（通过 `already_applied`），没有显式的 `merge` noop scenario。建议补充。

### M3. Fixture 命名约定

现有 fixture 命名为 `block-send-user-block-{applied,noop,rejected}.json`，新 sync fixture 的命名约定未在 spec 中定义。建议在 `tdx-provider-replay-fixtures/spec.md` 中补充 sync fixture 的命名模式（如 `block-sync-{mode}-{outcome}.json`）。

### M4. `create_if_missing` + `dry_run` 的 `created_block` 语义

Design Decision 4 说 dry_run 时 "返回计划，不真实创建"。`sync` summary 中有 `created_block` 字段。建议明确 dry_run 下 `created_block` 的值应该是 `false`（没有真正创建）还是某种 planned 状态标识（如 `"planned"` 或 `"would_create"`），避免上层误判。

### M5. 缺少 `tdx-provider-block-sync` spec 的错误场景

`tdx-provider-block-sync/spec.md` 覆盖了正常路径（replace、merge、create_if_missing、dry_run），但缺少以下场景：
- 空_symbols_列表传入时的行为
- governance 探测（读状态）失败时的行为
- 底层 `create_sector` 成功但 `send_user_block` 失败时的行为（部分完成状态）

---

## LOW - 可选改进

### L1. `_normalize_stock_list` 的排序语义

`block_mutation.py:31-44` 中 `_normalize_stock_list` 对 stocks 排序（`sorted`）以支持集合比较。这对 governance 比较是正确的，但排序后的列表在 audit artifact 中可能与用户原始输入顺序不同。`audit_request` 中保留了原始列表，这很好，但建议在 artifact 中显式标注 `normalized: true/false` 以避免混淆。

### L2. Spec 版本号管理

`block_mutation.py` 使用 `BLOCK_MUTATION_SCHEMA_VERSION = "2026-05-02"`，但 fixture 文件中外层 `schema_version` 仍为 `"2026-04-28"`。新增 block sync 时应统一版本号策略，避免内外层版本不一致。

### L3. `request_label` 可考虑作为 optional human-readable tag

如果保留 `request_label`，建议明确定位为 optional human-readable tag（类似 annotation），不参与 governance 决策或 idempotency 比较。这样既保留可追溯性，又不增加治理复杂度。

---

## 总结

| 级别 | 数量 | 关键项 |
|------|------|--------|
| CRITICAL | 2 | Bridge 签名不兼容；前置 change 落地状态不明 |
| HIGH | 4 | request_label 不一致；show 字段缺失；dry-run audit 未明确；task 粒度 |
| MEDIUM | 5 | mutation_key 分层；merge noop；fixture 命名；created_block 语义；错误场景 |
| LOW | 3 | 排序标注；版本号；request_label 定位 |

**建议**：先解决 C1/C2（确认前置治理链真正可用），再逐一处理 HIGH 项后进入实现阶段。整体设计方向正确，上述问题主要是 spec 精确度和 task 分解的改进。
