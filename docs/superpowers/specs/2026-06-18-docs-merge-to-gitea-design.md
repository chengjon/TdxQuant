# Docs 合并到 Gitea john/tdxquant 设计

> 设计日期: 2026-06-18
> 范围: 仅 TdxQuant 用户端文档,内部开发文档不入 Gitea

## 1. 背景与目标

### 1.1 现状

- **本地仓库** `/opt/claude/TdxQuant`(origin: `git@github.com:chengjon/TdxQuant.git`)
  - `docs/` 下共 176 个被 git 追踪的文件,扁平加多层子目录混合
  - 内容类型混杂:用户端 API 文档、内部 provider contracts、设计计划、code 评审、stable snapshots(含 `.pyc`)、30+ 份红宝书 markdown 转换(总计 ~50MB)
  - 3 个 byte-identical 的 markitdown 副本文件(MD5 相同:`e0840d4500b904ff395fc2f817604772`)
  - 本地 `web_docs/sections/*.md`(15 个主题文件)是 Gitea 上 85 个编号化拆分文件的源集
  - 本地 `TdxQuant接口说明文档.md`(191KB)是 85 个拆分文件的原始总文档

- **Gitea 仓库** `192.168.123.104:3001/john/tdxquant`
  - 公开、面向最终用户、纯净的 TdxQuant SDK 用户手册
  - `docs/` 下 88 个扁平文件,前 85 个为 `00_INDEX.md` ~ `85_常见问题.md` 的编号化结构
  - 另含 `TdxQuant_功能清单.md` 与 `TdxQuant_数据能力清单.md`
  - 没有子目录,没有 archive,没有内部开发文档

### 1.2 目标

把本地 `docs/` 中**面向 TdxQuant 用户的内容**合并到 Gitea 仓库,同时:

1. 保留 Gitea 现有 85 份编号化结构作为主体
2. 把红宝书、通达信官方手册、外部参考等内容归档到 `docs/archive/` 子目录
3. 内部开发文档(contracts / plans / reviews / snapshots / superpowers)**不入 Gitea**,保留在本地
4. 删除 byte-identical 的重复副本
5. 本地 `/opt/claude/TdxQuant` 仓库本次合并后**保持原样**,不做改动

## 2. 最终 Gitea 结构

```
docs/
├── 00_INDEX.md                                ← 重建,加入 archive 区段
├── 01_TdxQuant概述.md ~ 85_常见问题.md       ← 现有 85 个编号化文件
├── TdxQuant_功能清单.md                       ← 保持不变
├── TdxQuant_数据能力清单.md                   ← 与本地 18KB 版本智能合并
├── TdxQuant_接口说明文档_完整版.md            ← NEW: 本地 191KB 总文档,作为完整参考
└── archive/
    ├── README.md                              ← archive 区总索引
    ├── 红宝书/                                ← 30+ 份通达信官方手册 markdown 转换
    │   ├── README.md
    │   ├── 红宝书1-报表分析.md
    │   ├── 红宝书2-预警系统.md
    │   ├── 红宝书3-选股器和指标评测.md
    │   ├── 红宝书4-指标使用与分析.md
    │   ├── 红宝书5-定制版面.md
    │   ├── 红宝书6-定制品种.md
    │   ├── 红宝书7-系统设置.md
    │   ├── 红宝书8-公式系统_初级_.md
    │   ├── 红宝书9-公式系统_中级_.md
    │   ├── 红宝书10-公式系统_高级_.md
    │   ├── 红宝书11-公式系统_答疑_.md
    │   ├── 红宝书12-自定义数据.md
    │   ├── 红宝书15-策略股票池.md
    │   ├── 红宝书20-资金流向功能.md
    │   ├── 红宝书21-决策模型.md
    │   ├── 红宝书22-发现功能.md
    │   ├── 红宝书24-专业财务函数.md
    │   ├── 红宝书29-组合分析.md
    │   ├── 红宝书31-板块指数分析.md
    │   ├── 红宝书32-主题投资分析.md
    │   ├── 红宝书38-通达信灵活屏.md
    │   ├── 红宝书40-公式系统_专业财务数据_.md
    │   ├── 红宝书41-公式系统_新函数_.md
    │   ├── 红宝书42-智赢公式系统.md
    │   ├── 红宝书45-因子和策略评测指标.md
    │   ├── 红宝书46-特灵策略交易.md
    │   ├── 红宝书47-快枪手交易.md
    │   ├── 红宝书-期货相关功能操作.md
    │   ├── 红宝书-期货看盘和下单简要说明.md
    │   ├── 红宝书-港股相关功能操作2.md
    │   ├── 红宝书-通达信行情系统计算规则解释.md
    │   └── (与本地一致,共 31 份)
    ├── 通达信官方手册/                        ← TDX 平台参考文档
    │   ├── README.md
    │   ├── 通达信手机APP操作手册.md
    │   ├── 通达信板块指数和行业分类.md
    │   ├── 通达信热点板块白皮书.md
    │   ├── 通达信特色指数编制规则.md
    │   ├── 通达信波动率指数.md
    │   ├── 通达信商品指数.md
    │   └── 通达信技术分析之左侧交易与右侧交易.md
    ├── 指数与数据/                            ← 外部参考文章
    │   ├── README.md
    │   ├── RSRTDX-data.md
    │   └── 基金池使用说明.md
    └── markitdown工具/                        ← 本地转换工具文档(去重后)
        ├── README.md
        ├── TdxQuant_本地markitdown.md         ← 唯一保留的副本
        └── 转换质量报告.md
```

## 3. 文件分类决策表

### 3.1 入 Gitea(用户端 + 通达信生态参考)

| 本地路径 | Gitea 目标 | 处理方式 |
|---------|-----------|---------|
| `web_docs/sections/TdxQuant概述.md` 等 15 份 | 对应编号化文件 | 与 Gitea 现有版本智能合并(详见 §4) |
| `TdxQuant接口说明文档.md` (191KB) | `docs/TdxQuant_接口说明文档_完整版.md` | 新增,作为 85 份拆分版的完整参考 |
| `TdxQuant数据能力清单.md` (18KB) | `docs/TdxQuant_数据能力清单.md` (20KB) | 智能合并 |
| `红宝书*.md` (31 份) | `docs/archive/红宝书/` | 直接复制 |
| `通达信*.md` (7 份) | `docs/archive/通达信官方手册/` | 直接复制 |
| `RSRTDX-data.md`, `基金池使用说明.md` | `docs/archive/指数与数据/` | 直接复制 |
| `TdxQuant_本地markitdown.md` (1 份,去重后) | `docs/archive/markitdown工具/` | 直接复制 |
| `转换质量报告.md` | `docs/archive/markitdown工具/` | 直接复制 |

### 3.2 不入 Gitea(保留在本地 `/opt/claude/TdxQuant/docs/`)

**内部状态/规划文档**:
- `TdxQuant_API_System_Plan.md`
- `TdxQuant_Integration_Questions.md`
- `TdxQuant_Integration_Questions_Quantix.md`
- `TdxQuant_Interface_Coverage_Matrix.md`
- `TdxQuant_MyStocks_Next_Steps.md`
- `TdxQuant_Next_Steps.md`
- `TdxQuant_Project_Function_Map.md`
- `TdxQuant_tdx_functional_surface_merge.md`

**Provider-facing 内部 contracts** (12 份):
- `TdxQuant_Provider_Block_Mutation_Safety.md`
- `TdxQuant_Provider_Block_Sync_Contract.md`
- `TdxQuant_Provider_Capability_Discovery.md`
- `TdxQuant_Provider_Formula_Screen_Contract.md`
- `TdxQuant_Provider_Query_Contract.md`
- `TdxQuant_Provider_Replay_Fixtures.md`
- `TdxQuant_Provider_Result_Contract.md`
- `TdxQuant_Provider_Subscription_Event_Contract.md`
- `TdxQuant_Task_Subscription_Watch_Contract.md`
- `TdxQuant_Desktop_Trade_Audit_Contract.md`
- `TdxQuant_Trade_Audit_Lookup_Contract.md`
- `TdxQuant_Trade_Audit_Report_Contract.md`

**内部过程文档**:
- `pa-sect-read.md`, `pingan-tdx-win32-validation-summary.md`
- `tdx-hid-handoff-2026-04-23.md`, `tdx-hid-keyboard-plan.md`
- `tdx-plugin-dll-function-reference.md`, `tdx-windows-bridge-plan.md`
- `tdx_design_plan.md`, `win32-auto.md`
- `review-provider-query-contract-hardening.md`, `review2md-skill-guide.md`

**子目录整体保留本地**:
- `adr/` (Architecture Decision Records)
- `agents/` (Agent 配置)
- `reviews/` (代码评审)
- `superpowers/` (specs/plans/reviews)
- `stable-snapshots/` (含 `.pyc` 和 v1/v2 代码快照)
- `trading/` (desktop trade 扩展能力)
- `web_docs/` (源数据,合并后保留本地)

### 3.3 删除(byte-identical 重复副本)

本地以下两份与 `TdxQuant_本地markitdown.md` 完全相同(MD5: `e0840d4500b904ff395fc2f817604772`),不入 Gitea:
- `TdxQuant_本地markitdown工具.md`
- `TdxQuant_本地转换.md`

(注:本次合并**不动本地仓库**,故仅记录待后续清理,不在本次执行删除)

## 4. 智能合并策略(针对 85 份编号化文件)

### 4.1 比较流程

对每个 Gitea 编号文件,在本地 `web_docs/sections/` 中找对应主题:

- 若本地版本严格等于或为 Gitea 版本的子集 → 保持 Gitea 版本不变
- 若本地版本包含 Gitea 版本没有的内容(例如 `公众号文章例子` 本地 60KB vs Gitea 28KB) → 用本地版本覆盖,生成 diff 报告
- 若两边差异较大但都各有内容 → 标记为需人工评审,本次不合并,列入待办

### 4.2 已识别的差异点

| 文件 | Gitea 大小 | 本地对应 | 本地大小 | 处理 |
|------|----------|---------|---------|------|
| `82_公众号文章例子.md` | 28695 | `web_docs/sections/公众号文章例子.md` | 60305 | 用本地版本 |
| `TdxQuant_数据能力清单.md` | 20241 | `TdxQuant数据能力清单.md` | 18128 | 待 diff,人工裁决 |
| `06_通用函数.md` 等 13 个主题 | (各种) | `web_docs/sections/通用函数.md` 等 | (各种) | 待逐一 diff |

### 4.3 工具

使用 Python 脚本对每个文件做语义比较(行数、章节标题、是否为子集),输出 markdown 报告:

```
docs-merge-report.md
├── Identical (X files)
├── Local-superset (Y files) → 自动覆盖
├── Gitea-superset (Z files) → 不动
├── Divergent (W files) → 待人工裁决
```

## 5. 执行步骤

### Step 1: 准备工作区

```bash
# Clone Gitea 仓库到临时目录
git clone http://192.168.123.104:3001/john/tdxquant.git /tmp/tdxquant-gitea-merge
cd /tmp/tdxquant-gitea-merge
git config user.name "JohnC"
git config user.email "..."
```

### Step 2: 执行智能合并

对每个编号文件运行比较脚本(详见 §4),更新需要更新的文件。

### Step 3: 新增主文档

```bash
cp /opt/claude/TdxQuant/docs/TdxQuant接口说明文档.md \
   /tmp/tdxquant-gitea-merge/docs/TdxQuant_接口说明文档_完整版.md
```

### Step 4: 建立 archive 目录

```bash
mkdir -p docs/archive/{红宝书,通达信官方手册,指数与数据,markitdown工具}
# 按本设计 §2 与 §3.1 的清单复制文件
```

为每个 archive 子目录写 `README.md`,说明该目录的来源、用途和文件清单。

### Step 5: 更新 00_INDEX.md

在现有 `00_INDEX.md` 末尾追加:

```markdown
---

## 存档资料 (archive/)

以下为通达信官方文档、第三方参考资料与本地转换工具,供深入查阅:

- [archive/红宝书/](archive/红宝书/README.md) — 通达信官方手册 markdown 转换 (31 份)
- [archive/通达信官方手册/](archive/通达信官方手册/README.md) — TDX 平台参考文档 (7 份)
- [archive/指数与数据/](archive/指数与数据/README.md) — 外部参考文章 (2 份)
- [archive/markitdown工具/](archive/markitdown工具/README.md) — 本地转换工具文档

## 完整版参考

- [TdxQuant_接口说明文档_完整版.md](TdxQuant_接口说明文档_完整版.md) — 85 个拆分文件的原始合并版 (191KB)
```

### Step 6: Commit & Push

```bash
git add docs/
git commit -m "docs: consolidate local user-facing docs and add archive

- Smart-merge 85 numbered API docs with local web_docs/sections
- Add TdxQuant_接口说明文档_完整版.md (191KB master doc)
- Add docs/archive/ with 红宝书, 通达信官方手册, 指数与数据, markitdown工具
- Deduplicate byte-identical markitdown copies
- Internal dev contracts/plans/reviews excluded (kept in dev repo)"
git push origin main
```

### Step 7: 清理临时目录

```bash
cd /opt/claude/TdxQuant
rm -rf /tmp/tdxquant-gitea-merge
```

## 6. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 50MB 红宝书大幅增加 Gitea 仓库体积 | 用户已确认接受;后续如需可转 LFS |
| 智能合并误覆盖 Gitea 内容 | 仅在「本地严格超集」时自动覆盖;分歧项列入报告待人工裁决 |
| 推送凭证泄露 | 使用 Gitea Personal Access Token,不写入仓库或日志 |
| Gitea 推送中断 | 临时 clone 目录保留,可断点续推 |

## 7. 不在本本次范围

- 删除本地 2 个 markitdown 重复副本(记录在 §3.3,本次不动本地)
- 修改本地 `/opt/claude/TdxQuant` 仓库
- 内部开发文档的归档(本地保持原状)
- 修订 Gitea `TdxQuant_功能清单.md`(本次不动)
