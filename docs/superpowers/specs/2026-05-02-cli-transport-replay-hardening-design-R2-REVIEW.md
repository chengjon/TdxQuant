---
status: reviewed
files_reviewed: 1
critical: 0
warning: 2
info: 2
total: 4
reviewer: claude-opus-4-7
date: 2026-05-02
revision: R2 (post 0796b3a)
---

# Review (R2): CLI Transport Replay Hardening Design

Reviewed: `docs/superpowers/specs/2026-05-02-cli-transport-replay-hardening-design.md`
Revision: post-commit `0796b3a`

上一轮 review 的 9 个 finding (1 Critical + 6 Warning + 2 Info) 已全部确认收进 spec。本次是修订后全文复审，只报告新发现的问题。

---

### WARNING-1: 测试策略第 2 项仍用旧优先级措辞

**位置:** Testing Strategy, section 2, line 348

> `--fixture-path` 优先于 `--fixture`

CLI 层面 `--fixture` 和 `--fixture-path` 已经被 argparse 互斥组禁止同时出现，不可能出现"谁优先"的场景。这条测试用例的措辞会让读者以为两个参数可以共存，与 Argument Policy rule 3（互斥）矛盾。

**建议:** 改为三条独立测试用例：
- `--fixture` / `--fixture-path` 同时给出时 argparse 拒绝
- 单独给出 `--fixture` 时命中指定 built-in fixture
- 单独给出 `--fixture-path` 时命中指定外部路径

---

### WARNING-2: 缺少 `--output` replay 模式的专项测试

**位置:** Testing Strategy

Replay Argument Policy rule 7（line 187）和 stdout contract（line 198）都明确规定 `--output` 在 replay mode 下的行为：写出的 JSON 与 stdout 一致，不改变 transport contract。但 Testing Strategy 没有对应测试用例验证这一行为。

**建议:** 在 section 3 (Transport output contract tests) 中增加：
- replay mode 下同时使用 `--output` 时，stdout 仍输出单一 JSON envelope
- `--output` 写入的文件内容与 stdout JSON 一致

---

### INFO-1: Implementation Surface 术语不一致

**位置:** Implementation Surface, `tdxquant/cli.py` 职责, line 301

> 统一 fixture 选择优先级

Argument Policy rule 4 已经改为"选择算法"，这里仍写"优先级"。

**建议:** 改为"统一 fixture 选择算法"以与 rule 4 措辞对齐。

---

### INFO-2: 建议验证 `api send-user-block` nested 入口确实存在

**位置:** Supported Command Matrix, line 141

> `tdxquant api send-user-block --provider-mode replay`

`tdx-send-user-block` flat 命令在代码中有明确的 replay 支持（cli.py:1590），但 nested `api send-user-block` 的 replay dispatch 路径需要在实现前确认是否已经存在或者需要新增。根据 tdx-api-cli-entry spec 的 block write 场景描述，这个命令应该在 nested api 中存在，但值得在进入 implementation plan 前做一次代码确认。

---

## 总结

上一轮的 9 个问题已全部妥善处理。本轮复审只发现 2 个 Warning（测试策略措辞和缺失测试项）和 2 个 Info（术语一致性、命令存在性确认），均不阻塞进入 implementation plan。
