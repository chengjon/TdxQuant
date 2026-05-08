# Block Read Watchlist Snapshot Design — Review

Date: 2026-05-04
Reviewer: Claude (automated codebase-aware review)
Verdict: **Approve with suggestions**

---

## Summary

该设计填补了项目中的一个真实空白：只有 `watchlist -> block` 写路径（`sync_watchlist`），没有 `block -> watchlist snapshot` 读路径。设计定位清晰——provider-level 纯读能力，不与 task/export 混包，scope 控制得当。

以下分"必须修正"、"建议改进"、"肯定之处"三个层次展开。

---

## Must-Fix (必须在实施前解决)

### 1. `row_count` 命名有歧义

`data.snapshot.row_count` 的语义是"归一化后的 symbol 数量"，但 `row_count` 这个词暗示的是原始行数。当 `raw_member_count != row_count` 时，读者需要仔细对照文档才能理解差异。

**建议**: 改为 `symbol_count`，语义直接，不会和 raw row 概念混淆。

```
Before: row_count = 5  (normalized, not raw)
After:  symbol_count = 5  (clearly the final symbol count)
```

### 2. 未说明底层 API 调用路径

现有 `BlockApi` 有 `user_sectors()` 和 `send_user_block()` 但没有直接读取单个板块成员的方法。`read_watchlist_snapshot` 实际要调哪个 bridge 函数来获取板块成员列表？

对照现有代码：
- `tdxquant/api/meta.py:27` 有 `sector_stocks(block_code, block_type, list_type)`
- `query_contract.py` 已注册 `meta.sector_stocks` query shape

**需要明确**: `read_watchlist_snapshot` 是复用 `meta.sector_stocks` 再做归一化包装，还是走一条新的 bridge 调用路径？这直接影响实现复杂度和 replay fixture 设计。

### 3. 缺少与 `meta.sector_stocks` 的关系说明

`query_contract.py:52-60` 已有 `meta.sector_stocks` 的注册：

```python
"meta.sector_stocks": {
    "query_shapes": [{
        "query_kind": "meta.sector_stocks",
        "selectors": ["block_code"],
        "query_params": ["block_type", "list_type"],
    }],
    "supports_requested_fields": False,
```

设计文档应明确说明 `block.read_watchlist_snapshot` 与 `meta.sector_stocks` 的边界——是封装关系、替代关系、还是并行独立能力？避免上层用户困惑于该用哪个。

---

## Suggestions (建议改进，不阻塞合并)

### 4. `source_metadata.normalized` 字段冗余

`normalized: true` 在所有成功结果中都为 `true`。一个 always-true 的布尔字段不提供信息量——成功的定义本身就是"返回归一化快照"。

**建议**: 移除此字段。如果未来存在"部分归一化"场景，届时再加。

### 5. `source_metadata.deduplicated` 可用更有意义的字段替代

单纯的 `deduplicated: true/false` 只回答了"是否发生了去重"，但不如直接告诉上层"去重了多少"。

**建议**: 改为 `duplicate_count`（int，0 表示无重复），上层既能判断是否发生了去重，又能知道具体删了多少。

### 6. 缺少 `block_code` 输入校验的语义规则

设计定义了 "Missing Block" 和 "Empty Block" 两种情况，但没有覆盖 `block_code` 为空字符串、纯空白、或包含非法字符的情况。

**建议**: 在 Semantic Rules 中补充一条：

> If `block_code` is empty, blank, or contains characters outside the accepted block code format: return a stable validation failure (`success=false`), distinct from "missing block".

### 7. Capability Discovery 的 `query_metadata` 是新模式

现有 `provider_discovery.py` 的 `_capability()` 函数注册 metadata 使用 `stability`、`side_effect_level`、`entrypoints` 等固定字段。设计文档中引入的 `query_metadata` 子结构（`query_shapes`、`supports_empty_results` 等）在当前 provider_discovery 代码中没有先例。

**建议**: 要么确认 `query_metadata` 会复用 `query_contract.py` 的 `get_query_discovery_metadata()`，要么在设计文档中说明这是一个新的 discovery 扩展点，避免实现时产生两种不同的 metadata 注册方式。

### 8. 去重发生时是否应产生 `warnings`

设计规定去重后保留首次出现、丢弃后续重复项。但这种静默丢弃可能让上层不知道数据被修改了。

**建议**: 当 `deduplicated=true` 时，在 `warnings` 中追加一条提示，格式如：

```json
{"warnings": ["Deduplicated N repeated members in block ZXG"]}
```

这与现有 `sync_watchlist` 的 warning 语义一致。

### 9. 错误码未具体化

设计说 missing block 和 invalid member 都返回 `success=false` + "stable failure code"，但没有指明具体的 `ErrorCode`。

对照现有 `block_sync.py`:
- missing block: `ErrorCode.INVALID_REQUEST`
- 其他校验失败: `ErrorCode.INVALID_REQUEST`

**建议**: 在设计中明确 `code` 值，至少区分:
- missing block → 建议用 `ErrorCode.NOT_FOUND`（如果存在）或 `ErrorCode.INVALID_REQUEST`
- invalid member → `ErrorCode.INVALID_REQUEST` 或新增 `ErrorCode.NORMALIZATION_FAILED`
- blank block_code → `ErrorCode.INVALID_REQUEST`

这样上层可以根据 `code` 做分支处理，而不是 parse message。

---

## Affirmed (肯定之处)

1. **Scope 控制精准** — 纯读、单板块、不碰 task/export，v1 只锁定核心 contract。这与 `task-block-sync` 设计的"薄包装"哲学一脉相承。

2. **Missing Block ≠ Empty Block** — 这是最关键的设计决策。把 "不存在" 和 "存在但为空" 区分开，避免上层把"板块已删除"误读为"板块已清空"，从而触发破坏性操作。

3. **Invalid member 不静默跳过** — 严格策略正确。一个声称"归一化快照"的能力如果静默丢弃异常成员，等于承诺完整性却暗中违反。

4. **Order Preservation** — 保留原始顺序、不排序，信息损失最小。上层需要 set 语义时自己排序，但排序是不可逆的。

5. **Replay fixture 覆盖面** — 4 个 fixture（success / empty / missing / invalid）覆盖了 Semantic Rules 中定义的所有核心分支，直接可用于 contract 测试。

6. **CLI 命名一致** — `block-read-watchlist` 与现有 `block-sync` 命名风格对齐，flat CLI `tdx-block-read-watchlist` 也与 `tdx-block-sync` 保持一致。

---

## Checklist for Implementation

实施前请确认以下各项：

- [ ] 明确底层 bridge 调用路径（复用 `meta.sector_stocks` 或新路径）
- [ ] 说明与 `meta.sector_stocks` 的边界关系
- [ ] `row_count` → `symbol_count`（或给出保留命名的理由）
- [ ] 补充 `block_code` 输入校验规则
- [ ] 具体化各失败场景的 `ErrorCode`
- [ ] 确认 `query_metadata` 的注册方式是否与现有 discovery 基础设施对齐
- [ ] 决定是否在去重时追加 `warnings`
