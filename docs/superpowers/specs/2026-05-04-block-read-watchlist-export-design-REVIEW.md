# Block Read Watchlist Export Design — Review

Date: 2026-05-04
Reviewer: Claude (codebase-aware review)
Verdict: **Approve with suggestions**

---

## Summary

该设计在已稳定的 `block.read_watchlist_snapshot` provider capability 之上增加文件导出 task 层，定位清晰、scope 控制得当。独立 task 而非给现有 `task block-read-watchlist` 追加 `--output` 的决策正确——纯读与写文件是两种不同副作用语义。

以下分"设计问题"、"建议改进"、"肯定之处"展开。

---

## Issues (设计问题，建议修正后再实施)

### 1. `data.export.overwritten` 语义模糊

设计没有说明 `overwritten` 在以下情况下的取值：

- 新文件创建（目标不存在）→ `overwritten=false`？还是字段不存在？
- `--overwrite` 且目标存在 → `overwritten=true`
- `--overwrite` 但目标不存在 → `overwritten=false`？

**建议**: 明确定义：

| 场景 | `overwritten` |
|------|---------------|
| 新建文件 | `false` |
| 覆盖已有文件（需 `--overwrite`） | `true` |

永远输出此字段，不要用"存在/不存在"来传递语义。这样上层可以用 `overwritten` 做审计判断，无需推断。

### 2. JSON 序列化细节缺失

设计只说"以 JSON 原子写入"，但没有指定：

- **编码**: UTF-8 with BOM / without BOM？
- **缩进**: compact vs pretty-print？这直接影响 `bytes_written` 的值和人工可读性
- **中文处理**: snapshot 中 `sector_name` 包含中文（如 `"自选股"`）。如果不指定 `ensure_ascii=False`，JSON 序列化默认会输出 `\uXXXX` 转义，文件可读性差
- **key 排序**: 是否需要稳定排序以保证同内容同文件？

**建议**: 在 File Semantics 节补充一条 JSON 序列化规则：

```
- UTF-8, no BOM
- ensure_ascii=False
- indent=2 (可读性优先，V1 不考虑极致压缩)
- key 顺序保持 Python dict 插入序（snapshot 已有稳定字段顺序）
```

### 3. 失败时保留 `data.snapshot` 的契约应显式声明

设计说失败场景 2 和 3 "保留已读取成功的 `data.snapshot`"。这是一个有意义的 UX 决策，但需要明确：

- `data.snapshot` 存在 **不等于** 导出成功
- 上层必须以 `success` 字段判断最终状态
- 这是与纯读 `task block-read-watchlist` 的关键区别——纯读时 `data.snapshot` 存在即成功

**建议**: 在 Result Contract / Failure 节增加一条显式规则：

> When export fails after a successful snapshot read, `data.snapshot` is preserved for diagnostic purposes. Callers MUST NOT treat the presence of `data.snapshot` as evidence of a successful export. Always check `success` at the top level.

### 4. 未说明是否需要 flat CLI 入口

现有 `block.read_watchlist_snapshot` 有双层 CLI：

- nested: `tdxquant api block-read-watchlist --block-code ZXG`
- flat: `tdxquant tdx-block-read-watchlist --block-code ZXG`

本设计只提了 nested `task block-read-watchlist-export`，没有提到 flat CLI。

**建议**: 在 Scope 节明确说明是否需要 flat CLI（如 `tdx-task-block-read-watchlist-export`）。如果 V1 不加，在 Non-Goals 或 Open Questions 里注明。避免实现时产生歧义。

---

## Suggestions (建议改进，不阻塞合并)

### 5. `bytes_written` 字段的实用性存疑

`bytes_written` 取决于 JSON 序列化细节（缩进、中文编码方式），不反映逻辑内容大小。上层如果要验证写入完整性，用 content hash（如 SHA-256）更可靠；如果只是信息性展示，字段名改为 `file_size` 更直观。

**建议**: 二选一——

- 保留 `bytes_written` 但改名为 `file_size`，明确是物理文件大小
- 或替换为 `content_hash`（SHA-256 of written bytes），便于校验

### 6. 原子写入的临时文件命名和清理策略

设计说"在目标文件同目录创建临时文件"，但没有指定临时文件命名规则。实现时需考虑：

- 临时文件名应包含随机后缀或 PID，避免并发冲突
- 进程异常退出时（SIGKILL），临时文件可能残留
- 是否需要在启动时清理上次残留的临时文件？

**建议**: 补充一条简短说明：

> 临时文件使用 `tempfile.NamedTemporaryFile(dir=parent, suffix=".tmp", delete=False)` 或等价机制，命名包含随机字符串。V1 不实现启动时清理残留临时文件。

### 7. TOCTOU 竞态

"检查文件存在 → 决定是否覆盖" 和 "实际写入" 之间存在时间窗口。虽然原子 rename 减少了半成品风险，但 `--overwrite` 检查本身可以竞态。

V1 在单用户 CLI 场景下不太会遇到这个问题，但如果未来有并发调用风险，需要考虑。

**建议**: 不需要 V1 解决，但在设计中加一行 note 说明此限制即可。

### 8. Capability discovery 不适用

这是一个 task-layer 功能，不是 provider capability，所以不应出现在 `runtime.capabilities` 中。设计文档没有提到这一点，但也没有错误地把它放进 discovery。

**建议**: 在 Non-Goals 或设计说明中加一句："This task does not register as a provider capability and will not appear in `runtime.capabilities`." 防止实现者误加。

### 9. Replay / fixture 策略

设计没有提到 replay。task-block-sync 设计也没有专门的 task-layer replay（它依赖 provider-level replay），这个设计也可以采用同样策略。

**建议**: 补充一句："Export task 的 replay 行为取决于底层 `block.read_watchlist_snapshot` 的 replay 模式。task 层自身不新增独立 replay fixture。"

### 10. `--output` 路径校验不足

设计说 "父目录必须已存在"，但没有覆盖：

- `--output` 指向已有目录（而非文件路径）→ 应拒绝
- `--output` 是符号链接 → 是否 follow？
- `--output` 路径包含 `..` → 是否规范化？

**建议**: 在 File Semantics 节补充简短校验规则：

```
- --output 必须指向文件路径（不是目录）
- 父目录必须存在且可写
- 符号链接: follow（标准 os.path.realpath 行为）
- 路径规范化: 实现时应使用 os.path.realpath 解析
```

---

## Affirmed (肯定之处)

1. **独立 task 决策正确** — 纯读 vs 写文件是两种副作用语义，分开后错误 contract 更清晰，各自演进不互相污染。

2. **默认拒绝覆盖** — 安全默认值。导出场景下静默覆盖历史文件是常见数据丢失原因，显式 `--overwrite` 是正确选择。

3. **不 mkdir -p** — 保守且正确。隐式创建目录容易导致路径拼写错误静默通过，第一版要求显式准备目录是合理的。

4. **原子写入策略** — 同目录写临时文件 + rename 是标准的 safe-write 模式，能防止半截 JSON。

5. **只落盘 `data.snapshot`** — 不把整个 envelope（包括 task metadata）写入文件，保持了导出文件的纯粹性。上层如果需要 task 元数据可以查 stdout。

6. **错误不丢失 snapshot** — 读取成功但写入失败时保留 `data.snapshot`，上层可以诊断读取了什么但没写成什么。这是好的错误体验设计。

7. **与 task-block-sync 设计范式一致** — 同样是 thin task wrapper + 标准 task metadata 附加模式，不引入新的 task 协议。

8. **Non-Goals 覆盖充分** — CSV/Excel、catalog/preset、写回上层系统、task-only report schema 全部明确排除，scope 边界清晰。

---

## Checklist for Implementation

实施前请确认：

- [ ] 明确 `overwritten` 字段在所有场景下的取值（新建 / 覆盖 / 未覆盖）
- [ ] 补充 JSON 序列化规则（UTF-8, ensure_ascii=False, indent）
- [ ] 显式声明失败时 `data.snapshot` 不等于导出成功的契约规则
- [ ] 明确是否需要 flat CLI 入口
- [ ] 补充 `--output` 路径校验规则
- [ ] 补充临时文件命名策略说明
- [ ] 注明 capability discovery 不适用
- [ ] 注明 replay 策略依赖底层 provider
- [ ] 决定 `bytes_written` 是否改名或替换
