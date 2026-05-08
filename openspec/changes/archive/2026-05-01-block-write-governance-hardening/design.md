## Context

`block` 域已经完成了第一版安全包装：每次写操作都会返回 `block_mutation` 摘要、保留可选 `mutation_key`，并写本地 audit artifact。现在的问题是，这套包装仍然是“事后包装”而不是“写前治理”。系统不会先读取真实板块状态，也不会在“已经达到目标状态”或“当前状态与请求冲突”时做稳定决策，因此还不足以支撑 watchlist/block 同步这类需要可重复执行、可预测行为的上层场景。

现有读能力已经足够支撑治理：
- `block.user_sectors()` 可以识别板块是否存在及名称。
- `meta.sector_stocks(...)` 可以读取成员列表。

因此这一包不需要新增底层能力，而是要把已有读写能力组织成统一治理层。

## Goals / Non-Goals

**Goals:**
- 为全部五条 block 写路径引入统一治理决策：`applied / noop / rejected / failed`。
- 引入本地 `mutation_key` 幂等与冲突检测。
- 写前读取真实板块状态，根据目标状态与当前状态决定 `execute / skip / reject`。
- 扩展 `block_mutation` 与 audit artifact，补齐 machine-readable governance 字段。
- 为 `block` provider fixtures 补齐 `noop` / `rejected` 样例并用测试锁住 contract。

**Non-Goals:**
- 不新增 block 相关 CLI 命令。
- 不把治理扩展到读接口。
- 不引入跨进程分布式锁或外部状态存储。
- 不改变既有 `block` API 的入口命名。

## Decisions

### 1. 五条 block 写路径共用同一治理流水线

`create_sector`、`delete_sector`、`rename_sector`、`clear_sector`、`send_user_block` 都先经过同一治理入口，再决定是否调用底层写回调。统一顺序为：
1. 规范化请求摘要
2. 检查 `mutation_key`
3. 读取真实板块状态
4. 生成治理决策
5. 仅在 `execute` 时调用底层写操作
6. 无论结果如何都写 audit artifact

这样比各操作各自拼治理逻辑更稳，也能保证 `block_mutation` contract 一致。

### 2. “已达目标状态”统一定义为成功 `noop`

当前状态已经等于目标状态时，结果返回成功，但 `block_mutation.status = "noop"`，同时写审计。这样最适合上层同步场景：重复执行不会报错，也不会反复触发真实写入。

没有采用“已达目标状态即拒绝”的严格方案，因为那会让同步器必须对大量正常重复执行做额外分支。

### 3. `send_user_block` 按成员集合语义比较

`send_user_block` 的目标状态由成员集合定义：
- 忽略顺序
- 自动去重
- `show` 不参与目标状态比较

这比按列表顺序比较更符合 watchlist/block 同步场景，也能避免仅因顺序变化而重复写板块。

### 4. 缺失目标板块的语义按操作区分

- `delete_sector`：目标板块不存在视为 `noop`
- `rename_sector` / `clear_sector` / `send_user_block`：目标板块不存在视为 `rejected`
- `create_sector`：不存在则进入执行

这套规则让“删除不存在对象”保持幂等，同时避免对依赖目标板块存在的操作做含糊 fallback。

### 5. Audit artifact 覆盖所有治理结果

不仅 `applied` / `failed` 要写 audit，`noop` / `rejected` 也必须写。audit payload 与 `block_mutation` 一致，至少包含：
- `status`
- `governance_decision`
- `governance_reason`
- `desired_state`
- `observed_state`
- `request`
- `result`

这样排查“为什么没执行”时不需要依赖终端文案或重放现场状态。

## Risks / Trade-offs

- [治理前读取状态增加一次读调用] → 通过只在写路径引入，并用 targeted tests 锁住契约，接受这部分开销换取稳定性。
- [底层读取结果形状可能不稳定] → 在治理层先做规范化摘要，避免把原始 payload 直接变成 contract。
- [`mutation_key` 本地幂等只覆盖本机 artifact 范围] → 在 spec 中明确这是本地治理，不承诺跨主机全局幂等。

## Migration Plan

1. 保持现有 CLI / manager / bridge 入口不变。
2. 将 `apply_block_mutation_safety(...)` 升级为治理入口，由 bridge 传入真实写回调和所需读状态。
3. 扩展 `block_mutation` 和 audit artifact 的稳定字段。
4. 补充 `noop` / `rejected` representative fixtures。
5. 用 bridge/manager/CLI tests 锁住新决策语义。

## Open Questions

None. 设计边界已经锁定，本包只实现本地状态感知治理和审计收口。
