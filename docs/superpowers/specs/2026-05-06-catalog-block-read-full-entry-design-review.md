# Review: 2026-05-06-catalog-block-read-full-entry-design.md

**Type**: .md / arch | **Perspective**: architecture (auto) | **Date**: 2026-05-06 | **Reviewer**: Claude

---

## Executive Summary
一份精准的最小接入设计文档，正确识别了"只加一条 catalog entry，不改任何代码"的路径。所有引用实体经代码库验证存在，schema 约束与实际校验逻辑完全一致。无 HIGH 或 MED 问题。

## Document Metadata
| Field | Value |
|-------|-------|
| Source | docs/superpowers/specs/2026-05-06-catalog-block-read-full-entry-design.md |
| File Type | .md |
| Doc Type | arch (path: "design") |
| Sections | 12 |
| Referenced Files | 2 found / 0 missing |
| Referenced Symbols | 6 found / 0 missing |

## Evidence Verification

### Files Referenced
| File | Exists? | Location |
|------|---------|----------|
| `runtime/command-catalog.json` | yes | 33 entries, 225 lines |
| `tdxquant/catalog.py` | yes | catalog validation logic |

### Functions/Classes Referenced
| Symbol | Found? | Location |
|--------|--------|----------|
| `SUPPORTED_COMMAND_CATALOG_SOURCES` | yes | `catalog.py:8` — `frozenset({"report", "task", "trade"})` |
| `resolve_command_catalog_entry(...)` | yes | `catalog.py:60` |
| `catalog list` CLI | yes | `cli.py:579` |
| `catalog list --entry` | yes | `cli.py:583` |
| `catalog run` CLI | yes | `cli.py:588` |
| `read-zxg-full` preset | yes | `task-presets.json:88` |

### Claims Verified
| Claim | Status | Evidence |
|-------|--------|----------|
| "现有 schema 要求 source/preset/description/labels" | confirmed | catalog.py:72-89 validates exactly these 4 fields |
| "source 必须属于 SUPPORTED_COMMAND_CATALOG_SOURCES" | confirmed | catalog.py:76 with `{"report", "task", "trade"}` |
| "catalog 不直接执行 block-read-full" | confirmed | catalog run delegates to preset dispatch — no direct task execution in catalog.py |
| "`catalog list --entry` 已存在" | confirmed | cli.py:583 |
| "read-zxg-full preset 已存在" | confirmed | task-presets.json:88 |
| "不需要修改 catalog.py" | confirmed | catalog.py:60-94 is pure validation logic, new entry conforms to existing schema |
| "不需要修改 cli.py catalog dispatch" | confirmed | dispatch is generic — looks up entry, resolves preset, delegates |

## Checklist Results

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A1 | Component boundaries | PASS | 2 files改动（catalog JSON + tests），catalog.py/cli.py/provider/task 不动 |
| A2 | Data flow | PASS | catalog entry → preset lookup → task dispatch，委托链清晰 |
| A3 | Coupling | PASS | catalog 是 preset 的纯视图层，不复制参数、不重新执行 |
| A4 | Interface contracts | PASS | JSON 示例与现有 schema 完全一致 |
| A5 | Scalability | N/A | 单条 entry |
| A6 | Terminology consistency | PASS | 术语与代码库一致，命名模式 `read-<block>-full` 与 `export-<block>-watchlist` 对称 |
| A7 | Backward compatibility | PASS | append-only 到 command-catalog.json，不影响已有 33 条 entries |
| A8 | Implementation surface precision | PASS | 明确 3 个改动面 + 5 个"不需要修改"项 |
| A9 | Named entities verified | PASS | 全部 2 文件 + 6 符号确认存在 |

## Findings

### Critical Issues

None.

### Medium Issues

None.

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Implementation Surface (line 182) | "如有必要的 usage docs" 措辞模糊 | 其他 sections 都很精确（明确文件名、函数名），唯独这条是"如有必要" | 改为明确判断：是追加到现有 README / usage doc，还是不需要（因为 catalog list 已自描述） |
| 2 | Decision 3 (line 112-123) | 未引用直接先例 `export-zxg-watchlist` | command-catalog.json:218-223 已有完全相同的 task-source preset-backed pattern，与本文 propose 的 `read-zxg-full` 结构一致 | 在 Context 或 Decision 中引用此先例，增强"复用已有模式"的说服力 |
| 3 | Error Semantics (line 155-171) | 错误场景与 catalog.py 校验逻辑未逐条映射 | catalog.py:68-84 的具体校验（KeyError → ValueError, source 非字符串 → ValueError, source 不在 allowlist → ValueError, preset 缺失 → ValueError）与文档中的错误列表基本对应但措辞不同 | 非阻塞，当前描述已足够清晰 |

## Strengths

- **零代码改动**：整个 change 只是 JSON 数据 + tests，完全不动 Python 代码。这是 catalog 体系设计良好的直接证据。
- **Decision 结构清晰**：5 个 Decision 各自独立、有明确 rationale，比单一 "Recommended Approach" 段更易审查。
- **Error semantics 段**：明确列出所有失败路径和错误归属，减少实现时的歧义。
- **先例对齐**：JSON 示例中的 source/preset/description/labels 字段顺序与 command-catalog.json 中现有 entries 一致。

## Detailed Recommendations

- 在 Context 中加一句："`export-zxg-watchlist` (command-catalog.json:218) 是 task-source preset-backed entry 的直接先例，本包复用相同 pattern。" 这让审查者和实现者一眼看到已有验证。

- "如有必要的 usage docs" 建议改为明确判断。如果 `catalog list` 已自描述 entry 信息，则不需要额外 doc，直接写"V1 不需要新增 usage doc，`catalog list --entry read-zxg-full` 已提供足够信息"。

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 5 | 所有声明与代码库一致，schema 约束经 catalog.py 验证确认 |
| Completeness | 5 | Goals/Non-Goals/Decisions/Error/Tests/Rationale 完整覆盖 |
| Codebase Alignment | 5 | JSON 示例与现有 33 条 entries 格式一致，零代码改动经代码验证可行 |
| Actionability | 5 | 实现面精确到文件级，测试边界明确 |
| Terminology Consistency | 5 | 与代码库术语完全一致 |
| **Overall** | **5.0** | |

## Verdict
APPROVE — 零代码改动的纯数据接入，schema 完全兼容，所有实体验证通过。无阻塞性问题。

This is a clean minimal-integration design that correctly identifies the path of least resistance.
