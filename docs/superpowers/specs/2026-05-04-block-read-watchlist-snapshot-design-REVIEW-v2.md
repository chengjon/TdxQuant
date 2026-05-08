# Block Read Watchlist Snapshot Design — Review v2

Date: 2026-05-04
Reviewer: Claude (codebase-aware review against live implementation)
Verdict: **Approve with minor corrections**

---

## Summary

该设计文档已经吸收了上一轮 review (REVIEW.md) 的全部 must-fix 和大部分 suggestions，且对应能力已在代码库中完整实现。本次审核对照设计文档与实际代码（`block_snapshot.py`, `bridge.py:1009-1042`, `provider_discovery.py:481-491`, `query_contract.py:62-71`, `replay_fixtures.py:169-195`），重点关注设计与实现的偏差。

整体评价：设计定位精准，scope 控制得当，实现与设计高度一致。以下问题均为可快速修正的偏差。

---

## Issues (设计与实现的偏差)

### 1. `query_metadata` 中的字段未实现

设计文档 Capability Discovery Metadata 节列出了以下字段：

```
query_metadata:
  returns_ordered_symbols: true
  deduplicates_members: true
  normalizes_symbols: true
```

但实际 `provider_discovery.py` 的 `_capability()` 函数通过 `get_query_discovery_metadata()` 自动生成的 `query_metadata` 只包含：

- `query_shapes`
- `supports_requested_fields`
- `supports_empty_results`
- `supports_replay`

这三个设计文档中列出的字段在代码中不存在。

**建议**: 从设计文档中移除这三个字段。它们属于行为描述，不是 discovery metadata——上层应通过阅读设计文档或 replay fixtures 了解这些语义，而非通过 runtime discovery。如果确实需要运行时暴露这些属性，需要在 `get_query_discovery_metadata()` 或 `_capability()` 中新增扩展点，但目前没有其他能力使用这种模式。

### 2. `query_shapes` 中的 `type` 字段名不一致

设计文档写的是：

```json
"query_shapes": [{ "type": "single_block_code" }]
```

实际 `query_contract.py:64-68` 是：

```python
"query_shapes": [{
    "query_kind": "block.read_watchlist_snapshot",
    "selectors": ["block_code"],
    "query_params": [],
}]
```

字段名是 `query_kind`，值是完整能力名，不是 `type: "single_block_code"`。

**建议**: 将设计文档中的 `query_shapes` 示例更新为与 `query_contract.py` 一致的形式。当前写法会让实现者以为需要注册一个新格式，实际上只需在 `_QUERY_CONTRACT_REGISTRY` 中加一个标准条目即可。

### 3. 实现是两步调用，设计描述略有偏差

设计文档 "Relationship To Existing Read APIs" 节说：

> V1 should be implemented as a normalized wrapper around the existing raw block-member read path

但实际 `bridge.py:1009-1042` 的实现是 **两步调用**：

1. `run_tdx_get_user_sector()` — 验证板块存在 + 获取 sector_name
2. `run_tdx_data_sector_stocks()` — 获取板块成员

不仅仅是包装 `meta.sector_stocks`，还需要先调 `user_sectors` 来区分 missing block vs empty block。

**建议**: 在 "Relationship To Existing Read APIs" 节补充说明：实现需要先查询 `user_sectors` 确认板块存在性，再查询 `sector_stocks` 获取成员列表。这一信息对理解实现复杂度和 replay fixture 设计至关重要。

### 4. 所有失败场景共用 `invalid_request` 错误码

设计与实现一致：missing block、invalid member、blank block_code 都返回 `ErrorCode.INVALID_REQUEST`。

上一轮 review 曾建议区分 `NOT_FOUND` vs `INVALID_REQUEST`，但设计选择不采纳。这是合理的简化——V1 保持一个 code，靠 `message` 区分具体原因。

**保留意见**: 如果未来上层需要根据错误码做自动化分支处理（例如 missing block 触发创建，invalid member 触发告警），共用 `INVALID_REQUEST` 会迫使他们 parse message 字符串。建议在设计中加一条 forward-looking note，说明 V2 可能需要拆分错误码。

### 5. Replay fixture #5 (invalid-block-code) 缺失

设计列出 5 个 fixture，其中 #5 `block-read-watchlist-invalid-block-code.json` 标注为 "optional but recommended"。

当前 `replay_fixtures.py` 只注册了 4 个 (#1-#4)。单测 `test_block_snapshot.py:test_blank_block_code_failure` 在纯逻辑层覆盖了 blank block_code 场景，但 replay 路径没有对应 fixture。

**建议**: 如果 blank/malformed block_code 在 replay 模式下也需测试，建议补充 fixture。如果确认 replay 只覆盖 bridge 层之后的场景（即 block_code 已经过上游校验），当前状态可接受，但建议在设计中注明这一决策。

---

## Confirmed (设计已被实现正确验证的部分)

1. **Response contract 完全一致** — `data.snapshot` 结构（`block_code`, `symbols`, `symbol_count`, `source`, `source_metadata`）与 `block_snapshot.py:72-83` 的实现完全匹配。

2. **`symbol_count` 命名** — 上一轮 must-fix 已修正，代码和设计一致使用 `symbol_count`。

3. **`duplicate_count` 替代 `deduplicated: bool`** — 上一轮 suggestion 已采纳，`block_snapshot.py:66` 正确输出 `duplicate_count` (int)。

4. **去重 warning** — `block_snapshot.py:65-66` 在 `duplicate_count > 0` 时追加 warning，格式与设计一致。

5. **`block_code` 输入校验** — `block_snapshot.py:37-42` 处理 blank block_code，返回 `INVALID_REQUEST`。对应 Semantic Rule 7。

6. **Order preservation** — `block_snapshot.py:50-62` 用 `seen: set` + `symbols: list` 保留首次出现顺序，与 Semantic Rule 3 一致。

7. **Invalid member 不静默跳过** — `block_snapshot.py:52-57` 遇到 non-normalizable member 立即返回失败，与 Semantic Rule 6 一致。

8. **Capability discovery 注册** — `provider_discovery.py:481-491` 正确注册了 `stability="stable"`, `side_effect_level="read_only"`, `supports_replay=true`，与设计一致。

9. **Query contract 注册** — `query_contract.py:62-71` 和 `query_contract.py:137` 正确注册了 query shapes 和 replay 支持。

10. **CLI 命名一致** — nested: `block-read-watchlist`, flat: `tdx-block-read-watchlist`，与 `block-sync` / `tdx-block-sync` 命名风格对齐。

---

## Assessment

| 维度 | 评价 |
|------|------|
| Scope 控制 | 精准。纯读、单板块、无 task/export |
| 与实现一致性 | 高。4 处偏差均为文档描述与代码细节的轻微不匹配 |
| 语义正确性 | 高。Missing ≠ Empty、invalid member 不静默跳过、order preservation 都是正确决策 |
| Replay fixture 覆盖 | 良好。4/5 fixture 已实现，#5 optional 缺失 |
| 可维护性 | 良好。`block_snapshot.py` 作为纯函数模块，测试覆盖充分 |
| 前向兼容 | 合理。错误码拆分、task wrapper、export 均留有明确的后续路径 |

---

## Checklist for Next Steps

- [ ] 从设计文档 `query_metadata` 中移除 `returns_ordered_symbols` / `deduplicates_members` / `normalizes_symbols`，或说明这些是行为描述而非 discovery 字段
- [ ] 将 `query_shapes` 示例从 `{ "type": "single_block_code" }` 更正为 `{ "query_kind": "block.read_watchlist_snapshot", "selectors": ["block_code"] }`
- [ ] 补充说明实现需要 `user_sectors` + `sector_stocks` 两步调用
- [ ] 考虑在设计中增加 forward-looking note，说明 V2 可能拆分错误码
- [ ] 决定是否补充 fixture #5 或在设计中注明 replay 不覆盖 block_code 校验场景
