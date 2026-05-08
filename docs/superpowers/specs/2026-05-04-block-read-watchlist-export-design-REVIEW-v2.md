# Block Read Watchlist Export Design — Re-Review

Date: 2026-05-04
Reviewer: Claude (second pass after revision)
Verdict: **Approved**

---

## Revision Check

上一轮 10 条反馈（4 issues + 6 suggestions）的采纳情况：

| # | 原始反馈 | 状态 | 采纳位置 |
|---|---------|------|---------|
| 1 | `overwritten` 语义模糊 | 已修正 | L104-107: 取值表 |
| 2 | JSON 序列化细节缺失 | 已修正 | L144-158: 完整序列化规则 |
| 3 | 失败时 `data.snapshot` 契约需显式声明 | 已修正 | L125-128: 明确声明 |
| 4 | flat CLI 入口未说明 | 已修正 | L33 Non-Goals + L76-80 显式排除 |
| 5 | `bytes_written` 改名 | 已修正 | L102: 改为 `file_size` |
| 6 | 临时文件命名策略 | 已修正 | L185-186 |
| 7 | TOCTOU note | 已修正 | L194 |
| 8 | capability discovery 不适用 | 已修正 | L196-201: 新增完整节 |
| 9 | replay 策略 | 已修正 | L200-201 |
| 10 | `--output` 路径校验 | 已修正 | L168-173 |

全部采纳，文档质量显著提升。

---

## Remaining Minor Notes (不阻塞，仅供参考)

### 1. 失败场景未指定 ErrorCode

设计定义了三类失败（snapshot 失败、路径冲突、写入失败），但没有为每类指定具体的 `code` 值。

对照现有模式（`block_sync.py`, `bridge.py`），建议在实施时遵循：

| 失败类别 | 建议 `code` |
|---------|------------|
| snapshot 读取失败 | 直接透传底层 provider failure code |
| 路径冲突（文件已存在，无 overwrite） | `ErrorCode.INVALID_REQUEST` |
| 路径无效（目录不存在、不可写、指向目录） | `ErrorCode.INVALID_REQUEST` |
| 写入失败（临时文件写失败、rename 失败） | `ErrorCode.EXECUTION_FAILED` |

这样上层可以做结构化分支处理，无需 parse message。

### 2. Python 方法签名未列出

设计提到了 `TdxTaskManager.block_read_watchlist_export(...)` 但没有给出完整参数列表。对照 task-block-sync 设计（显式列出了所有参数和默认值），建议实施时按以下签名对齐：

```python
def block_read_watchlist_export(
    self,
    *,
    block_code: str,
    output: str,
    overwrite: bool = False,
    show: bool = True,
) -> Result:
```

不阻塞——可在实施 plan 中补充。

### 3. `data.export.error` 字段类型未指定

Failure 节（L132）提到 `data.export` 中可保留 `error` 字段，但没有说明其类型（string? dict with `code` + `message`?）。

建议实施时保持为 string（简单诊断信息），与现有 `message` 字段风格一致。如果需要结构化错误，应在 V2 考虑。

---

## Final Assessment

| 维度 | 评价 |
|------|------|
| 问题覆盖 | 上一轮全部采纳 |
| Scope 控制 | 精准。独立 task、单文件 JSON、显式输出路径 |
| 副作用语义 | 清晰。纯读 vs 写文件分离正确 |
| 契约完整性 | 高。success/failure 各场景覆盖充分 |
| 文件安全性 | 高。原子写入、默认拒绝覆盖、不 mkdir -p |
| 实现就绪度 | 高。可直接进入实施 |

**Verdict: Approved.** 可以进入实施阶段。
