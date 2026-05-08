# Subscription Watch Bridge Integration Regression Design

Date: 2026-05-03
Topic: `subscription-watch-bridge-integration-regression`
Status: Draft for review

## Context

`subscription-watch` 当前已经具备完整的三层主线：

- foreground task run artifact contract
- worker-local background control
- worker HTTP bridge + master-side static registry

并且 resilience contract 也已经补齐到：

- `running / reconnecting / degraded / stopping`
- bounded reconnect + degraded low-frequency recovery
- same-`run_id` reconnect semantics

当前剩余的高价值缺口，不再是功能从 0 到 1，而是 **bridge / worker / master 三层联动的 integration regression hardening**：

- worker 本地状态是否稳定投射到 HTTP
- Master registry/client 是否稳定消费这些状态
- auth / allowlist / transport error / stale-state normalization 是否有端到端回归保护

## Goal

把现有 `subscription-watch` bridge control plane 从“有分层单测”推进到“有稳定跨层回归”的状态，重点锁住：

- worker-local background control
- bridge HTTP transport
- master-side registry/client
- CLI remote-control entrypoints

## Non-Goals

- 不新增 bridge endpoint
- 不新增 SSE / stream transport
- 不做 worker 自注册
- 不做多 worker 调度
- 不扩到 `trade`、`block`、`formula` 远控
- 不修改 foreground `subscription-watch` 的业务语义

## Chosen Scope

第一版只做现有 control plane 的 regression hardening：

- `bridge serve` worker 配置加载和守护行为
- `watch/start`
- `watch/stop`
- `watch/status`
- `watch/list`
- `watch/artifacts`
- `watch/events`
- `watch/logs`
- `health`
- Master registry/client 对以上能力的远程调用 contract
- CLI `bridge watch-*` / `bridge health` 的输出和错误语义

## Test Matrix

### 1. Worker-local -> HTTP bridge projection

重点验证：

- active `running`
- active `reconnecting`
- active `degraded`
- stale active state 归一为 `failed(stale_process_state)`
- terminal `completed / stopped / failed`

目标是确保：

- bridge 从不自行发明状态
- bridge 只投射 controller 读模型
- resilience 字段不会在 HTTP 层丢失

### 2. Auth and allowlist regression

重点验证：

- 缺失 `Authorization`
- 错 token
- source IP 不在 `master_allowlist`
- worker config 非法或缺字段

目标是确保：

- worker bridge 对未授权请求稳定拒绝
- 不把鉴权失败伪装成业务失败

### 3. Master registry / client regression

重点验证：

- 静态 registry 加载
- worker 选择与 `worker_id` 解析
- worker 不存在
- worker HTTP error body 转换
- JSON parse failure
- timeout / connection refused 等 transport failures

目标是确保：

- Master 端错误稳定、可诊断
- 不把 transport failure 混成 task failure

### 4. CLI remote-control regression

重点验证：

- `bridge serve --config ...`
- `bridge watch-start`
- `bridge watch-stop`
- `bridge watch-status`
- `bridge watch-list`
- `bridge watch-artifacts`
- `bridge watch-events`
- `bridge watch-logs`
- `bridge health`

目标是确保：

- CLI 继续只是 transport entrypoint
- stdout JSON / exit code 与 registry/client contract 对齐

## Key Risks

### 1. Bridge tests多，但跨层 coverage 仍然不够

当前已有：

- controller focused tests
- bridge request-handler tests
- registry tests

但这些仍偏分层。缺的是“以 Master 调 worker 的真实组合方式”验证：

- worker config
- HTTP server
- registry client
- CLI entrypoint

### 2. Resilience 字段容易在 transport 层丢失

`heartbeat_at`、`last_event_ts`、`reconnect_count`、`degraded_since`、`last_error` 是新 contract 字段。  
如果没有跨层 regression，它们容易只在 task 层存在，而在 bridge/master/CLI 视角被遗漏。

### 3. allowlist / auth 容易只有 happy-path coverage

当前安全边界已存在，但更接近功能验证而不是完整回归矩阵。  
这条包要把 negative-path 也锁住。

## Proposed Deliverables

### 1. Bridge integration fixture helpers

新增一组专供 integration regression 的 helper：

- active run status samples
- reconnecting / degraded status samples
- stale state samples
- registry error samples

它们不是 provider replay fixture，而是 bridge/control-plane integration fixture。

### 2. End-to-end bridge regression suite

新增一套以“Master 调 worker”为中心的测试：

- 起本地 bridge server
- 注入 worker controller 状态
- 通过 registry/client 走真实 HTTP
- 再由 CLI 命令封一层

### 3. Docs refresh

补文档说明：

- 当前 bridge control plane 的稳定边界
- 哪些字段是 machine contract
- 哪些错误属于 auth / transport / background control / task runtime

## Open Questions

### 1. `health` 是否要继续只看 bridge 自身在线，还是合并更多 worker runtime 摘要？

第一版建议：

- 保持 `health` 轻量
- 只保证 bridge 自身可达 + background control 可用
- 不把更重的 task runtime summary 再塞进 `health`

这样范围更稳。
