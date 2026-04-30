## Context

当前 `trade_audit` 聚合入口已经具备三类稳定过滤能力：

- `broker`
- `methods`
- `statuses`

并且日常入口已经覆盖了：

- 单方法异常视角
- 跨方法 submit-path 异常视角

但还没有把 `broker + methods + statuses` 这一组真正三维的过滤组合固化为稳定 preset / catalog / bundle。由于桌面交易当前只稳定支持 `pingan`，最自然的第一步是先把 `pingan + submit path + exceptions` 收成固定入口，为后续多券商扩展保留稳定命名模式。

## Goals / Non-Goals

**Goals:**

- 为 `trade_audit` report preset 增加第一组 broker-scoped submit-path exception 入口
- 为 command catalog 增加对应 entry 和 diagnostics / follow-up bundle
- 保持现有 `broker`、`methods`、`statuses` 底层语义不变
- 用最小变更把三维过滤正式产品化

**Non-Goals:**

- 不新增新的底层 trade/task workflow
- 不修改 `trade_audit` 过滤逻辑
- 不一次性铺开所有 broker / method / status 组合矩阵
- 不引入多 broker OR 过滤

## Decisions

### 1. 第一组 broker-scoped 组合固定为 `pingan + submit path + exceptions`

固定组合：

- `broker=pingan`
- `methods=["buy_submit_once", "confirm_current"]`
- `statuses=["rejected", "failed"]`

原因：

- 当前稳定券商主线就是 `pingan`
- submit path 是最自然的跨方法组合视角
- 与已有跨 broker submit-path preset 保持语义对照，便于未来扩展

### 2. 继续只在 preset / catalog 层扩展，不改底层过滤 contract

这包不会新增 Python 参数，也不会修改 CLI 参数解析。

原因：

- `broker`、`methods`、`statuses` 已经可用
- 当前缺口是日常入口产品化，而不是底层能力缺失
- 保持范围小，可以避免无意义回归

### 3. follow-up bundle 继续挂在现有 confirm workflow 上

新增 follow-up bundle 会复用：

- `task-confirm-current`
- 新的 broker-scoped submit-path exception audit entry

原因：

- 与现有 split-step confirm follow-up 体系保持一致
- 能直接把 broker-scoped 异常视角串进当前日常排障路径

## Risks / Trade-offs

- [当前 broker 只有 `pingan`，显得像重复入口] → 这是有意的稳定命名预铺，避免未来多券商时再重构命名
- [preset / catalog 数量继续增长] → 这包只加一组高价值三维组合，不铺满矩阵
- [用户混淆“跨 broker submit-path”和“pingan submit-path”] → 在文档和描述里显式标明 broker-scoped
