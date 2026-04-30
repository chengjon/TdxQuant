## Context

当前 catalog 已具备：

- entry 统一索引
- bundle 顺序编排
- bundle 局部 step 选择
- execution plan 预览

缺口在于发现性不足。随着 entry / bundle 数量继续增长，单靠名字难以表达“这是开盘前用的”“这是排障用的”。

## Goals / Non-Goals

**Goals:**

- 为 entry 和 bundle 提供稳定、可维护的标签元数据。
- 支持通过 `catalog list --label ...` 筛选。
- 补一组带标签的默认 bundle，使 catalog 更贴近日常阶段性使用。

**Non-Goals:**

- 不做多标签布尔表达式。
- 不改单条执行、bundle 执行或 plan 执行语义。
- 不引入新的 workflow 类型。

## Decisions

### 1. entry / bundle 都支持可选 `labels`

配置结构扩展：

- `labels`: 字符串数组，可选

约束：

- 每个标签必须是非空字符串
- 同一 entry / bundle 内标签去重

### 2. `catalog list --label <name>` 做简单单标签过滤

先做最小可用模型：

- `catalog list --label morning`
- `catalog list --kind bundle --label diagnostics`

过滤规则：

- 仅返回包含该标签的条目
- `kind=all` 时分别对 entries / bundles 过滤

### 3. 默认补一组更贴近日常的 bundle

在现有基础上扩展：

- `morning-review`
- `failure-review`
- `guarded-trade-followup`
- `submit-once-followup`

这些 bundle 只复用既有 entry，不新增 workflow。

### 4. 先补缺失的高频 report entry

当前已有 `recent-failures` report preset，但 catalog 里没有对应 entry。为了让排障 bundle 更自然，本轮补上：

- `recent-failures`

## Risks / Trade-offs

- [标签体系过于随意] → 先从少量高频标签开始，保持简单。
- [默认 bundle 仍然主观] → 只补最明显的日常套路，后续再按真实使用继续迭代。
