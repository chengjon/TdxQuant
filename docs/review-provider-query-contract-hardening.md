# Spec Review: provider-query-contract-hardening

**Review Date:** 2026-05-03
**Reviewer:** Claude
**Scope:** proposal, design, 5 spec files, tasks

---

## Overall Verdict

Spec direction is sound and well-scoped. "共性元数据 + domain-native rows 保留" is the right tradeoff. Below are issues that should be resolved before implementation begins.

---

## Strengths

1. **Non-goals are clearly articulated** — 不新增查询命令、不压统一 row schema、不改 envelope，有效防止 scope creep。
2. **Decision 5 (envelope 不变)** — 正确地将改动限定在 `data` payload 层，回滚风险最小。
3. **Replay fixtures 作为 contract locker** — 比附属样例的定位更准确，能锁住回归基线。
4. **Task breakdown 三段式合理** — metadata → CLI/replay alignment → discovery/docs/verification，依赖关系清晰。

---

## Issues

### P0 — Must fix before implementation

#### 1. `query_kind` 稳定字面量未定义

spec 多处要求使用 "provider-owned stable literal"，但整条 change 没有给出任何具体的 `query_kind` 值。

- `market.snapshot` → `query_kind` 是什么？`"market_snapshot"` ? `"snapshot"` ?
- `meta.stock_list` → `"stock_list"` ? `"meta_stock_list"` ?
- `financial.financial_data` 和 `financial.financial_data_by_date` 用同一个 `query_kind` 还是区分？

**Risk:** 各 capability 自行发明字面量，导致上层 adapter 无法真正统一消费。

**Recommendation:** 在 design.md 或 tdx-provider-query-contract spec 中新增一个 `query_kind` 注册表，至少列出 16 个 covered capability 的具体值。命名建议用 `{domain}.{method}` 格式与 capability name 对齐（如 `market.snapshot`, `financial.financial_data`）。

#### 2. `requested_fields` 语义歧义

Manager 层已有 `_resolve_fields` 方法，会将用户传入的 fields 转换为实际请求字段。spec 没有澄清：

- `requested_fields` = 用户原始传入的字段？
- `requested_fields` = 经过 `_resolve_fields` 解析后的字段？
- `returned_fields` = `requested_fields` 的子集？还是 bridge 层实际返回的字段名？

**Risk:** 实现者各自理解，导致 contract 不一致。

**Recommendation:** 明确定义：
- `requested_fields`: 调用者显式传入的字段列表（经 normalize 后），若用户未指定则记录为 `["*"]` 或 `[]`。
- `returned_fields`: 实际 payload rows 中出现的字段名（从第一条 row 的 keys 提取，或从 bridge 返回的 header 提取）。

#### 3. Meta capability 的 selector 字段覆盖不全

design.md 列出的条件字段为 `symbol / symbols / date / date_range / market / block_code`，但 Meta API 有多个方法的参数不在其中：

| 方法 | 主要参数 | 能否被现有条件字段覆盖 |
|------|----------|----------------------|
| `stock_list` | market, list_type | `market` 可覆盖，`list_type` 无法覆盖 |
| `sector_list` | list_type | 无对应条件字段 |
| `sector_stocks` | block_code, block_type, list_type | `block_code` 可覆盖，其余不行 |
| `divid_factors` | stock_code, start_time, end_time | 可用 `symbol` + `date_range` |
| `ipo_info` | ipo_type, ipo_date | `date` 部分可覆盖，`ipo_type` 无法覆盖 |
| `gb_info` | stock_code, date_list, count | `symbol` 可覆盖，`date_list` / `count` 不行 |
| `gp_one_data` | stock_list, field_list | `symbols` 可覆盖 |

**Risk:** 大量 Meta 方法的主要参数没有对应的 selector 字段，上层仍需按方法特例消费。

**Recommendation:** 两种方案选一：
- **(A) 扩充条件字段**：增加 `list_type`, `ipo_type`, `count` 等通用 selector。
- **(B) 增加 `query_params` catch-all**：对于无法归入共性字段的方法参数，统一放入 `query_params: dict` 保留完整参数快照。方案 B 更务实，推荐。

---

### P1 — Should fix before implementation

#### 4. Capability discovery spec 过于薄

`tdx-provider-capability-discovery` spec 只有 2 个 scenario，没有定义具体 metadata shape。现有 `_capability()` helper 的签名是固定的（name, domain, description, stability, side_effect_level, entrypoints），没有 `query_shapes` / `supports_requested_fields` 等字段。

**Questions to answer:**
- `query_shapes` 是一个 list 还是一个 dict？每个 shape 包含哪些字段？
- 这些 metadata 是扩展 `_capability()` 函数的参数，还是作为 extra dict 合并？
- 是否需要新增 `query_metadata` 子结构，类似 formula screen 的 `data.summary`？

**Recommendation:** 在 discovery spec 中增加一个 metadata shape 示例：
```python
{
  "query_shapes": [{"query_kind": "market.snapshot", "selector": "symbol"}],
  "supports_requested_fields": true,
  "supports_empty_results": true,
  "supports_replay": true,
}
```

#### 5. `data` payload 布局与现有 manager metadata 的关系不清

Manager 层通过 `attach_manager_metadata` 已经在 `data` 中注入 `manager_meta`。查询元数据 (`query_kind`, `row_count` 等) 是与 `manager_meta` 同级还是嵌套在 `manager_meta` 内？

从 `provider-result-success.json` 看，当前 `data` 只有 `rows`。新增的 query metadata 会变成：

```json
{
  "data": {
    "rows": [...],
    "query_kind": "market.snapshot",
    "row_count": 5,
    "requested_fields": ["price", "volume"],
    "returned_fields": ["price", "volume", "amount"]
  }
}
```

**Risk:** 扁平放在 `data` 根层级容易与 rows 的字段名冲突（如某个 capability 的 row 恰好有 `query_kind` 字段）。

**Recommendation:** 将查询元数据包裹在 `data.query_meta` 子结构中，与 `rows` 分离：
```json
{
  "data": {
    "query_meta": { "query_kind": "...", "row_count": 5, ... },
    "rows": [...]
  }
}
```
这也与 formula-screen fixture 中 `data.summary` + `data.rows` 的已有模式一致。

#### 6. `stock_code` vs `stock_list` 参数映射

Market API 的单 symbol 方法用 `stock_code: str`，而 Financial/Transaction 用 `stock_list: list[str]`。spec 要求 "不混用 `symbol` 和 `symbols`"，但没有说明映射规则：

- `market.snapshot(stock_code="000001.SZ")` → metadata 中应该是 `symbol: "000001.SZ"` 还是 `symbols: ["000001.SZ"]`？
- `financial.financial_data(stock_list=["000001.SZ", "600519.SH"])` → 用 `symbols: [...]`?

**Recommendation:** 明确规则：当底层参数是单值时用 `symbol`，当底层参数是列表时用 `symbols`。即使单值列表也保持区分。

---

### P2 — Nice to fix, can defer

#### 7. Market.kline 未出现在主要 scenario 中

`market.kline` 是多 symbol + 时间范围查询，参数复杂度最高（stock_list, period, start_time, end_time, count, dividend_type, field_list, fill_data），但 spec 只展示了 single-symbol 和 date-range scenario。

**Recommendation:** 至少在 design.md 的 Risks 部分补充 kline 的 selector 映射方案，或在 spec 中增加一个 kline scenario。

#### 8. Fixture 数量估算和边界

4 domains × 3 outcomes (success/empty/failure) × 平均 2-3 方法 = ~24-36 fixtures。spec 说 "representative" 但没有指定每个 domain 至少覆盖哪些方法。

**Recommendation:** 在 tasks.md 2.2 中列出每个 domain 的最低 fixture 覆盖清单（如 market: snapshot + kline; meta: stock_list + sector_stocks; financial: financial_data; transaction: stock_transaction_data）。

#### 9. schema_version / capability_version 变更策略

新增 `data` 内字段是 additive change，但 spec 没有提到是否需要更新 `schema_version` 日期或 `capability_version`（当前是 `"v1"`）。

**Recommendation:** 保持 `v1` 不变，在 `schema_version` 中使用当前日期（与 formula screen 的 `"2026-04-28"` 模式一致）。在 design.md Decisions 中补充一条。

#### 10. Empty result 的 `requested_fields` / `returned_fields` 行为

当查询成功但无匹配 rows 时，`returned_fields` 是 `[]` 还是与 `requested_fields` 相同？没有 rows 就无法从数据推断实际返回字段。

**Recommendation:** 明确 empty result 时 `returned_fields = []`，`requested_fields` 保持调用者传入的值。

---

## Tasks Assessment

tasks.md 的三段式结构合理，但有具体改进建议：

| Task | 建议 |
|------|------|
| 1.1 | 补充 `query_kind` 注册表作为 1.1 的交付物之一 |
| 1.2 | 明确 metadata 注入点是 bridge 层返回 Result 后、还是 manager proxy 包装时 |
| 1.3 | 指定至少覆盖哪些方法（建议 snapshot + kline + stock_list + financial_data + stock_transaction_data） |
| 2.2 | 给出每个 domain 的最低 fixture 清单 |
| 2.3 | 明确 test 文件位置和测试方式（contract test vs integration test） |
| 3.1 | 补充 `query_shapes` 的具体 shape 定义 |
| 3.2 | 在 roadmap docs 中标注这是 hardening change，不引入 breaking change |

---

## Summary

Spec 方向正确，范围克制。核心问题是 **`query_kind` 字面量未注册**、**`requested_fields` 语义未定义**、**Meta 方法参数覆盖不全**。建议先补充这三项再进入实现。
