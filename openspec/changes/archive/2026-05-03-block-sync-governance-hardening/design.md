## Context

`block write governance` 已经把 TongDaXin 自定义板块写操作的治理入口收到了 `block_mutation` 模块：它支持写前读取真实状态、`applied / noop / rejected / failed` 决策，以及稳定 audit artifact。问题是，bridge 五条 block 写路径还没有完整迁移到这套“写前治理 + 延迟执行回调”模式，所以上层今天仍不能把它当作真正完成的治理底座使用。

如果直接让上层反复调用 `send_user_block(...)`，就会把同步语义留给调用方自行处理：

- `replace` 与 `merge` 的差异
- 目标板块不存在时是拒绝、自动创建还是只返回计划
- dry-run 只返回 diff 而不真实写入
- `mutation_key` 在整个同步请求层面的 replay / conflict 规则
- 变更 diff 的稳定 machine-readable 结果

因此，这一包要同时做两件事：

1. 补齐 bridge 五条 block 写路径对当前 `apply_block_mutation_safety(...)` 签名和治理模式的真实接入。
2. 在此基础上新增一条 `block sync` capability，并把底层真实写入继续交给现有 `block_mutation` 治理链。

## Goals / Non-Goals

**Goals**

- 为单向 `watchlist -> TongDaXin block` 同步定义稳定 provider contract。
- 同时支持 `replace` 与 `merge`，默认 `replace`。
- 支持 `create_if_missing`，默认 `false`。
- 支持 `dry_run`，默认 `false`，并返回完整 diff 与治理决策。
- 明确 `show` 作为执行选项存在，默认 `true`，但不参与同步目标状态比较。
- 让 `mutation_key` 在 sync request 层面支持 replay / conflict 决策。
- 继续复用现有 `block_mutation` 治理字段和 audit artifact。
- 为 manager / CLI / replay fixtures 补齐对应入口。

**Non-Goals**

- 不做双向同步：`TongDaXin block -> 上层 watchlist`。
- 不做 watchlist 文件导入解析；第一版只接受标准化 `symbols` 列表。
- 不新增 task / preset / catalog 场景入口。
- 不引入远程 bridge / HTTP worker 控制；这条线仍属于 provider capability。
- 不扩展新的 block 低层 runtime 能力。

## Decisions

### 1. `block sync` 是独立 capability，而不是继续扩 `send_user_block`

`send_user_block` 保持“单次板块写入”定位；`block sync` 负责“同步意图 -> diff -> 治理决策 -> 真实写入/只返回计划”。这样能把同步语义和普通写语义分开，避免后续 provider contract 继续变脏。

对外入口：

- Python：`TdxApiManager.block.sync_watchlist(...)`
- Nested CLI：`tdxquant api block-sync ...`
- Flat CLI：`tdx-block-sync ...`

### 2. Request contract 只接受标准化 `symbols`

第一版输入固定为：

- `block_code`
- `symbols`
- `mode`
- `create_if_missing`
- `dry_run`
- `show`
- `mutation_key`

`symbols` 在进入治理前做 canonical normalization：

- 去重
- 过滤空值
- 统一股票代码格式

`show` 作为执行选项保留，默认 `true`，但它不参与同步目标状态比较，也不进入 sync-level idempotency 比较的 canonical symbol-set diff 逻辑。

这样第一版先把同步治理 contract 固定下来，再把 CSV / JSON / watchlist 文件导入放到下一层场景任务。

### 3. `replace` 与 `merge` 使用明确目标状态语义

- `replace`
  - `desired_symbols = requested_symbols`
  - 允许产生 `removed_symbols`
- `merge`
  - `desired_symbols = observed_symbols ∪ requested_symbols`
  - `removed_symbols` 必须始终为空

`replace` 更适合强同步；`merge` 更适合低风险补入。默认 `replace`，因为它更接近“上层 watchlist 与目标 block 强一致”的直觉。

### 4. `create_if_missing` 默认关闭，但作为显式开关存在

- block 不存在 + `create_if_missing=false` -> `rejected`
- block 不存在 + `create_if_missing=true`
  - `dry_run=true` -> 返回计划，不真实创建
  - `dry_run=false` -> 先创建 block，再执行同步

不允许隐式创建。这样既支持完整同步流程，又不会把“自动建板块”变成默认副作用。

### 5. `dry_run` 走完整决策流，但绝不触发真实写入

`dry_run=true` 时，系统仍然：

1. 规范化请求
2. 读取当前状态
3. 计算 `desired/observed/add/remove/unchanged`
4. 做治理决策
5. 写审计 artifact

唯一差异是最后不执行真实写入。这样 `dry_run` 与 live 结果只差最后一步，不容易发生 contract 漂移。

`dry_run` 仍然写审计 artifact。这样“为什么将执行/为什么将拒绝”的依据可以在不做真实写入时仍然被稳定回放和审计。

### 6. Result contract 以 sync summary 为主，保留底层 mutation metadata

结果以 `data.sync` 为同步主视角，至少包含：

- `block_code`
- `mode`
- `create_if_missing`
- `dry_run`
- `show`
- `status`
- `governance_decision`
- `governance_reason`
- `created_block`
- `would_create_block`
- `added_symbols`
- `removed_symbols`
- `unchanged_symbols`
- `desired_symbols`
- `observed_symbols`

同时保留 `data.block_mutation` 作为底层治理 metadata。这让上层同步器只需看 `sync` 字段，只有调试或审计时才需要深入到底层 mutation。

其中：

- `created_block=true` 只表示真实执行中已经创建了 block
- `dry_run=true` 时 `created_block` 必须为 `false`
- 如果 dry-run 规划中会创建 block，则 `would_create_block=true`

### 7. `mutation_key` 在 sync request 层做幂等与冲突检测

`mutation_key` 的比较对象不是某一次单独写操作，而是整个 canonical sync request：

- 同 key + 同 canonical request -> 允许 replay / short-circuit
- 同 key + 不同 canonical request -> `rejected`

这样幂等语义更符合“同步一次 watchlist 到某个 block”的业务含义。

sync-level `mutation_key` 不直接复用为底层每一步 write 的 `mutation_key`。底层治理仍保有自己的 mutation identity 与 artifact；sync 层通过关联 metadata 把这些底层结果挂到同一次 sync outcome 下。这样可以避免“一个 sync request 包两步写入”时底层 idempotency 语义相互污染。

### 8. 真实写入继续复用现有 `block_mutation` 治理链

当 `dry_run=false` 且需要执行时：

- 如需建板块，调用 `create_sector` 的治理链
- 最终成员写入调用 `send_user_block` 的治理链

`block sync` 自己不重新发明底层写安全，只负责：

- 计算同步目标
- 生成 sync 决策
- 组织底层 mutation 结果与审计

但在进入 `block sync` 实现之前，这一包必须先补齐 bridge 五条 block 写路径对当前 `apply_block_mutation_safety(...)` 签名的适配：

- 传入真实 `observed_state` probe
- 传入延迟执行的 `execute_write` callback
- 不允许“先写后包装”

## Risks / Trade-offs

- [sync contract 与普通 mutation contract 可能重叠]  
  通过明确 `data.sync` 为主、`data.block_mutation` 为底层 metadata 来分层，避免职责混乱。

- [`create_if_missing + dry_run` 语义容易含糊]  
  通过区分 `created_block` 与 `would_create_block`，避免把预演与真实创建混淆。

- [`merge` 与 `replace` 未来可能需要更多模式]  
  第一版只做两种最常见语义，避免过早引入 `patch`/`remove-only` 等复杂模式。

- [同步层重复使用 `mutation_key` 可能与底层写请求 key 概念冲突]  
  在设计中明确：sync capability 的 `mutation_key` 绑定的是 canonical sync request，不直接复用为底层每一步 write 的 mutation key。

- [前置 block-write 治理变更在 bridge 层落地不完整]  
  通过把 bridge 五条写路径的签名适配与治理模式切换纳入本 change 的显式任务，避免同步能力建立在错误前提上。

## Migration Plan

1. 先补齐 bridge 五条 block 写路径对当前 `apply_block_mutation_safety(...)` 签名与治理模式的接入。
2. 新增 `block sync` orchestration 层。
3. 在 manager 与 CLI 暴露新入口，不改变现有 block write 入口。
4. 在 replay fixtures 中加入 representative sync samples。
5. 用 targeted tests 锁住 `replace`、`merge`、`create_if_missing`、`dry_run`、`mutation_key` 等 contract。
6. 更新 Function Map / Next Steps，把 block 同步从“规划层”推进到“正式 capability”。

## Open Questions

None. 当前范围已经锁定为单向同步、标准化 symbols 输入、provider capability 先行。
