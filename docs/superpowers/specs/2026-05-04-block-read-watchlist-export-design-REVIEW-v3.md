# Block Read Watchlist Export Design — Independent Review v3

Date: 2026-05-05
Reviewer: Sisyphus (independent review, post-approval)
Verdict: **Approved — 1 concern, 2 suggestions, no blockers**

---

## Preamble

This is a third-pass review conducted after two prior review cycles already concluded with "Approved." The design has been revised to address all 10 items from Review v1 and 3 minor notes from Review v2. This review evaluates the *final* document (262 lines) on its own merits, with awareness of prior feedback but no obligation to re-litigate resolved items.

---

## Concern (non-blocking but worth tracking)

### C1. `overwrite=false` 的 no-clobber 原子语义实现复杂度被低估

设计在第 216-218 行明确要求：

> `overwrite=false` 必须使用等价的 no-clobber 原子发布语义。如果目标文件在 publish 之前或 publish 过程中出现，必须稳定失败。

这在 Linux 上可以自然实现（`os.open` with `O_CREAT | O_EXCL` → `os.rename` 或直接在 fd 上写入），但在 Windows 上 `os.rename` 会静默覆盖目标文件。当前项目虽然面向 Linux（TongDaXin 量化环境），但设计文档没有显式标注平台假设。

更重要的是，`O_EXCL` + `rename` 本身也有细微窗口：`O_EXCL` 创建临时文件是原子的，但 `rename` 覆盖目标在 Linux 上也是原子的——所以 `overwrite=false` 的真正正确做法应该是：

1. 在目标路径直接 `O_CREAT | O_EXCL` 创建文件（而非临时文件 rename）
2. 写入数据
3. close

这牺牲了"失败时不留下任何文件"的保证（创建成功但写入中途失败会留下空/半截文件），但严格满足了 no-clobber 要求。

**设计当前的方案是**：先写临时文件，再 rename。对于 `overwrite=true` 这没问题，但对于 `overwrite=false`，`rename` 在 Linux 上会覆盖已存在的目标——除非实现先 `os.link` + `os.unlink` 或使用 `renameat2` with `RENAME_NOREPLACE`（Linux 3.15+，Python 无直接绑定）。

**建议**：实施时针对 `overwrite=false` 路径单独验证原子语义是否能通过标准库实现。如果需要 `O_EXCL` 直写而非 temp+rename，设计文档应更新原子写入策略一节，区分 `overwrite=true` 和 `overwrite=false` 两条实现路径。不阻塞——在 PLAN 阶段解决即可。

---

## Suggestions (不阻塞)

### S1. `data.export.error` 字段建议扩展为结构化错误

设计第 147-148 行确定 V1 使用简单字符串。这个决策对 V1 合理，但建议在文档中增加一行展望：

> V2 可考虑将 `data.export.error` 扩展为 `{ code: str, message: str }` 结构化对象，与顶层 Result 的 `code` / `message` 模式保持一致。

这样实现者在设计 `data.export` 的数据类时可以预留字段，避免 V2 扩展时的破坏性变更。

### S2. 测试节缺少并发竞态测试的实现指导

设计第 242 行要求：

> `overwrite=false` 时，如果目标文件在最终发布前被并发创建，必须稳定失败为 existing-file conflict

这是一个正确的要求，但实现和测试都有难度。建议在测试节增加一条说明：

> 并发竞态测试可使用 `threading` 或 `multiprocessing` 在 publish 窗口内创建目标文件，验证 task 稳定失败。如果平台不支持可靠的竞态注入，可标记为 `@pytest.mark.skipif` 并在 CI 中以 `xfail` 形式记录。

这防止实现者因"测试无法可靠构造竞态"而跳过该测试项。

---

## Affirmed (设计亮点，保持不变)

1. **独立 task 的 scope 控制精确。** 纯读与写文件分开，错误契约不互相污染，后续扩 CSV 或批量导出有自然演进空间。

2. **原子写入 + 默认拒绝覆盖的组合安全且实用。** 同目录临时文件 + rename 是成熟的 safe-write 模式，配合显式 `--overwrite` 避免了静默数据丢失。

3. **失败时保留 `data.snapshot` 的决策是好的错误体验。** 上层可以诊断"读了什么但没写成什么"，而不是只看到一个失败码。

4. **JSON 序列化规则完整且合理。** UTF-8、no BOM、`ensure_ascii=False`、`indent=2` 四条规则保证了可读性和确定性。

5. **Result contract 的 failure 分类清晰。** 三类失败（snapshot 失败、路径冲突、写入失败）各自有明确的 `code` 建议，上层可以结构化分支处理。

6. **Non-Goals 边界明确。** CSV/Excel、catalog/preset、flat CLI、capability discovery 全部显式排除，防止 scope creep。

7. **经过两轮评审修订后的文档质量高。** 10 条 Review v1 反馈和 3 条 Review v2 notes 全部采纳，文档已具备直接进入 PLAN 阶段的条件。

---

## Verdict

**Approved.** 设计可以进入实施阶段。Concern C1（no-clobber 原子语义的平台和实现细节）建议在 PLAN 阶段首先验证，确认标准库能否满足设计要求的原子性保证。
