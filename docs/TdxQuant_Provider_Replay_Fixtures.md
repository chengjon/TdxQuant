# TdxQuant Provider Replay Fixtures

本文定义 TdxQuant 当前内置的 provider replay fixture bundle。

它的目标不是模拟 live runtime，而是提供一组稳定、仓内自带、可直接被上层项目消费的 contract fixtures，用于：

- contract test
- 离线联调
- replay 样例
- fake provider 输入资产

## 1. Current Scope

当前 fixture bundle 覆盖这些高价值 provider contract：

- 通用同步 provider result success / failure
- `formula.screen` success / failure
- `runtime.capabilities`
- `runtime.health`
- `runtime.doctor`
- `block.send_user_block` 的 mutation safety 结果（applied / noop / rejected）
- provider-level subscription event rows
- `subscription-watch` run artifact bundle

支持两种格式：

- `json`
- `jsonl`

## 2. Stable Location

当前内置 fixture 位于：

- `tdxquant/fixtures/provider/`

推荐通过 loader helper 使用，而不是在上层项目里硬编码目录结构。

## 3. Loader Helpers

当前稳定 helper 位于：

- `tdxquant.replay_fixtures`
- `tdxquant.replay_provider`

可用函数：

- `list_provider_replay_fixtures()`
- `get_provider_replay_fixture_path(name)`
- `load_provider_replay_fixture(name)`
- `execute_sync_replay(capability, ...)`
- `materialize_subscription_watch_replay(paths=..., ...)`

其中：

- `list_provider_replay_fixtures()` 返回 fixture manifest
- `get_provider_replay_fixture_path(name)` 返回绝对路径
- `load_provider_replay_fixture(name)` 自动按 `json` 或 `jsonl` 解析
- `execute_sync_replay(...)` 把内置 fixture 或显式 JSON 文件物化成同步 provider `Result`
- `materialize_subscription_watch_replay(...)` 把 built-in bundle 或显式 run artifact 目录物化成新的 completed run

## 4. Current Fixture Names

当前第一版固定这些名字：

- `provider-result-success`
- `provider-result-failure`
- `formula-screen-success`
- `formula-screen-failure`
- `runtime-capabilities-success`
- `runtime-health-degraded`
- `runtime-doctor-degraded`
- `block-send-user-block-applied`
- `block-send-user-block-noop`
- `block-send-user-block-rejected`
- `subscription-event-batch`
- `subscription-watch-events`
- `subscription-watch-status-completed`
- `subscription-watch-summary-completed`
- `subscription-watch-manifest`

这些名字应被视为对上层稳定的 sample 标识。

## 5. Replay Mode Entry Points

截至 `2026-05-02`，fixture bundle 已经不再只是静态样例，而是可以通过正式入口跑成 in-process replay mode。

当前支持的同步 replay capability：

- `formula.screen`
- `runtime.capabilities`
- `runtime.health`
- `runtime.doctor`
- `block.send_user_block`

当前支持的运行入口：

- Python manager
  - `TdxApiManager(..., provider_mode="replay")`
  - `TdxApiManager(..., provider_mode="replay", replay_fixture="formula-screen-failure")`
  - `TdxApiManager(..., provider_mode="replay", replay_fixture_path="/tmp/custom.json")`
- nested CLI
  - supported:
    - `tdxquant api capabilities --provider-mode replay`
    - `tdxquant api health --provider-mode replay`
    - `tdxquant api doctor --provider-mode replay`
    - `tdxquant api formula-screen --provider-mode replay`
    - `tdxquant api send-user-block --provider-mode replay`
  - explicit reject example:
    - `tdxquant api snapshot --provider-mode replay`
- flat CLI
  - supported:
    - `tdxquant tdx-capabilities --provider-mode replay`
    - `tdxquant tdx-health --provider-mode replay`
    - `tdxquant tdx-doctor --provider-mode replay`
    - `tdxquant tdx-formula-screen --provider-mode replay`
    - `tdxquant tdx-send-user-block --provider-mode replay`
  - explicit reject example:
    - `tdxquant tdx-data-kline --provider-mode replay`
- task
  - `tdxquant task subscription-watch --provider-mode replay`

fixture 选择规则：

- selector precedence:
  - `--fixture-path <json/jsonl-or-run-dir>`: 使用显式路径输入
  - `--fixture <builtin-name>`: 使用显式 built-in fixture 名称
  - 默认：按 capability 自动选 built-in fixture
- Python 侧还支持 capability-keyed `replay_fixture_map`

replay mode 的安全语义：

- 不支持的 capability 直接稳定拒绝
- fixture 缺失或格式错误直接稳定拒绝
- replay mode 不允许 silent fallback 到 live Windows runtime

CLI subprocess replay contract：

- nested `api` replay command 在 CLI 层先过支持矩阵；不支持时直接返回 `INVALID_REQUEST`，并在 `data.replay_source` 里带上 `mode=replay` 与被拒绝的 capability 推断值
- flat `tdx-*` replay command 只对当前支持矩阵做 replay dispatch；未纳入矩阵的命令会返回 `unsupported replay flat command: ...`
- `task subscription-watch --provider-mode replay` 只走 replay bundle materialization；replay source 有问题时返回稳定失败结果，不会打开 live session
- `--output <path>` 会把和 stdout 完全相同的 JSON payload 镜像写入文件，包括 replay 失败 payload；stdout 与文件内容应视为同一 contract 的两个出口

## 6. Python Example

```python
from tdxquant import list_provider_replay_fixtures, load_provider_replay_fixture

fixtures = list_provider_replay_fixtures()
formula_payload = load_provider_replay_fixture("formula-screen-success")
event_rows = load_provider_replay_fixture("subscription-event-batch")
watch_summary = load_provider_replay_fixture("subscription-watch-summary-completed")
```

其中：

- `formula_payload` 是一个 provider-facing JSON dict
- `event_rows` 是按源顺序解析后的 `list[dict]`
- `watch_summary` 是 `subscription-watch` 结束后的 stable run summary

所有同步 JSON fixture 现在都遵循 hardened envelope：

- 顶层使用 `success`
- 同时保留兼容别名 `ok`
- `warnings` 和 `artifacts` 固定为数组
- `data` 固定为对象

其中 discovery fixtures 额外锁定这些字段：

- `runtime-capabilities-success`
  - `data.summary.total`
  - `data.summary.by_domain`
  - `data.summary.by_stability`
  - `data.summary.by_side_effect_level`
  - `data.grading.stability_levels`
  - `data.grading.side_effect_levels`
- `runtime-health-degraded`
  - `data.context`
  - `data.checks`
  - `data.recommended_actions`
  - `data.recommended_action_items`
- `runtime-doctor-degraded`
  - `data.findings`
  - `data.recommended_action_items`
  - finding-level `related_checks`
  - finding-level `recommended_action_id`

其中 `subscription-watch` fixtures 额外锁定这些结构：

- `subscription-watch-events`
  - canonical `events.jsonl`
  - `capability`
  - `run_id`
  - `sequence`
  - `reconnect_metadata`
- `subscription-watch-status-completed`
  - `state`
  - `output_paths`
  - `stop_reason`
- `subscription-watch-summary-completed`
  - `final_state`
  - `stop_reason`
  - `artifacts`
- `subscription-watch-manifest`
  - `capability_version`
  - `requested_symbols`
  - `output_dir`

其中 `block mutation` fixtures 额外锁定这些结构：

- `block-send-user-block-applied`
  - `governance_decision`
  - `governance_reason`
  - `desired_state`
  - `observed_state`
- `block-send-user-block-noop`
  - `status=noop`
  - `governance_decision=skip`
  - `governance_reason=already_applied`
- `block-send-user-block-rejected`
  - `status=rejected`
  - `governance_decision=reject`
  - `governance_reason=missing_block`

## 7. Subscription Watch Replay

`subscription-watch` 在 replay mode 下不是模拟长连接，而是立即物化一份 completed run artifact bundle：

- `manifest.json`
- `status.json`
- `summary.json`
- `events.jsonl`
- `events.csv`

当前支持两种来源：

- built-in completed-run fixture bundle
- 显式 replay manifest 路径或 replay run 目录

物化时会统一重写：

- `run_id`
- `output_dir`
- `output_paths`
- `artifacts.*_path`
- `events.jsonl` 中每一行的 `run_id`

这意味着 replay source 只是输入资产，不会把旧 run 的路径原样泄露到新 run 结果里。

## 8. Current Boundary

这包当前已经解决：

- 内置 fixture 资产
- 稳定 fixture 名称
- 统一 loader
- JSON / JSONL contract test 基座
- in-process fake provider mode
- `subscription-watch` completed-run replay materialization

这包当前还没有解决：

- HTTP replay 服务
- daemon fake provider
- live subscription session / delayed playback 模拟
- 更大范围 capability 覆盖
- start / stop / status 形态的测试控制面

这些属于后续更高一层的 fake provider / integration hardening 工作。
