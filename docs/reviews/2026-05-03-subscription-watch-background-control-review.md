# Subscription Watch Background Control - 方案审核意见

> 审核日期: 2026-05-03
> 审核范围: Design spec、Implementation plan、已落地的源码与测试

---

## 总体评价

方案整体设计成熟，契约边界清晰，代码与设计文档的对齐度很高。核心架构决策——将前台 run artifact contract 与后台进程治理分层处理——是合理的。测试覆盖了大部分边界情况，尤其是 reconcile 逻辑和 stop 信号竞态的处理比较扎实。

以下按严重程度分级列出发现的问题。

---

## P0 - 需要修复的问题

### 1. 启动超时返回值语义模糊

**位置**: `subscription_watch_background.py:556-557`

```python
if startup_state is None:
    return self._current_start_result(payload)
```

当 `_wait_for_startup_state` 超时返回 `None` 时，`start()` 返回 `ok: True` 且 state 仍为 `starting`。调用方无法区分"启动成功但还在初始化"和"启动超时、进程可能卡死"。

**建议**: 超时应返回错误结果，例如:

```python
if startup_state is None:
    return {
        "ok": False,
        "error": {
            "code": "START_TIMEOUT",
            "message": "subscription-watch runner did not reach running state within timeout",
            "details": payload,
        },
    }
```

### 2. Schema version 不一致

**位置**: `subscription_event.py:9` vs `subscription_watch_run.py:8`

- `subscription_event.py`: `SUBSCRIPTION_EVENT_SCHEMA_VERSION = "2026-04-28"`
- `subscription_watch_run.py`: `SUBSCRIPTION_WATCH_SCHEMA_VERSION = "2026-05-01"`

同一个 run 的 events.jsonl 事件行带 `schema_version: "2026-04-28"`，但 status.json / summary.json / manifest.json 带 `schema_version: "2026-05-01"`。设计文档未说明这两个 version 的关系和各自的生命周期。

**建议**: 统一为一个 schema version，或在设计文档中明确说明 event 行和 run artifact 的 schema version 可以独立演进的理由。

### 3. stop 后存在 runner 终态写入竞态

**位置**: `subscription_watch_background.py:638-646`

stop 发送 SIGTERM 后等待进程退出，然后调用 `reconcile_background_state`。但 runner 的 finally 块也会调用 `write_terminal_background_state`。如果 reconcile 在 runner finally 之前执行，会看到 stale 状态并覆盖 active.json，随后 runner 的 finally 又再次覆盖。

测试 `test_stop_does_not_overwrite_fast_runner_terminal_payload` 覆盖了 runner 在 signal 回调中写入的场景，但未覆盖 runner 在进程退出后才写入 finally 的场景。

**建议**: 在 reconcile 发现 process 已退出后增加短暂等待或重试，确认 active.json 已被 runner 最终写入后再返回结果。或改为在 stop 中只发信号并等待进程退出，然后仅做一次 reconcile。

---

## P1 - 建议改进

### 4. status.json 中 `output_paths` 与 `artifacts` 字段冗余

**位置**: `tdxquant/api/task.py:1447-1459`

`build_subscription_watch_status_payload` 写入 `output_paths`，但 `build_status_payload` 又通过 `payload.update()` 追加了 `artifacts` 字段。两者包含相同的路径信息，但 key 不同（`output_paths` 用 `events_jsonl_path`，`artifacts` 也用 `events_jsonl_path`）。消费方需要判断读哪个。

**建议**: 统一为一个字段。设计文档中 status.json 的定义是 `output_paths`，建议移除 task.py 中额外注入的 `artifacts`。

### 5. manifest.json 缺少 `runner_log_path`

**位置**: `subscription_watch_run.py:48-72`

`SubscriptionWatchRunPaths` 包含 `runner_log_path`，runner 确实会写入这个文件。但 `build_subscription_watch_manifest` 的 `artifacts` 字典中没有包含它。调用方无法通过 manifest 发现 runner 日志的位置。

**建议**: 在 manifest.artifacts 中加入 `runner_log_path`。

### 6. reconcile 函数有隐含写副作用

**位置**: `subscription_watch_background.py:119-179`

函数名为 `reconcile_background_state`，暗示只读或只做轻量修正。但实际上它会调用 `_normalize_terminal_payload` 写入 `active.json` 并删除 `pid` 文件。调用方如果只期望读取当前状态，会意外修改文件系统状态。

**建议**: 要么将函数重命名为体现写语义的名称（如 `reconcile_and_persist_background_state`），要么将读和写分离。

### 7. CSV 并非真正 optional

**位置**: 设计文档第 59 行 vs `tdxquant/api/task.py:1475-1503`

设计文档说 `events.csv` 如果存在才从 JSONL 投影而来。但代码中 `append_event_rows` 总是写入 CSV 文件。`events_csv_path` 始终存在于 `SubscriptionWatchRunPaths` 中。

**建议**: 如果 CSV 确实是可选的，应通过参数控制是否写入。如果决定始终写入，则更新设计文档。

### 8. run_id 碰撞时 mkdir 会直接失败

**位置**: `tdxquant/api/task.py:1269`

```python
run_paths.run_dir.mkdir(parents=True, exist_ok=False)
```

如果上一次崩溃留下了一个 run_id 目录（例如进程在 mkdir 后、写入 manifest 前崩溃），后续用相同 run_id 重跑会直接抛 `FileExistsError`，但没有任何有意义的错误信息。

**建议**: 捕获 `FileExistsError` 并返回明确的错误 Result，包含建议的 next_action（如让调用方不传 run_id 让系统自动生成）。

---

## P2 - 可优化项

### 9. 缺少进程心跳 / 健康检查

当前 runner 只在启动和终止时更新 `active.json`。如果 runner 进程在运行过程中死锁（例如回调卡住），reconcile 只能等到 PID 不再存活才能检测到异常。对于长时间运行的 subscription-watch，这个窗口可能很大。

**建议**: 考虑在 runner 中增加定期心跳（例如每 30 秒更新 `active.json` 的 `updated_at`），reconcile 检查 `updated_at` 超时来判断僵尸状态。

### 10. 无旧 run 目录清理机制

每次运行生成独立的 `run_id` 目录，但没有清理策略。长时间使用后 `runtime/subscription-watch/` 下可能积累大量目录和事件文件。

**建议**: 后续版本考虑增加基于时间或数量的自动清理策略。当前阶段可在文档中标明这一点。

### 11. 测试覆盖缺口

以下场景缺少测试:

- **runner 正常完成路径**: `test_subscription_watch_background_runner.py` 只测试了异常和中断路径，没有测试 runner 正常执行完成、`active.json` 最终为 `completed` 的场景。
- **stop 时 runner 已自行完成**: 当 stop 发现进程已退出且 state 为 `completed` 时，应返回 `completed` 而非 `stopped`。
- **并发 start 请求**: 虽然 `ALREADY_RUNNING` 和幂等键有测试，但没有测试两个几乎同时的 start 请求（非幂等）的竞态行为。

### 12. 信号处理仅覆盖 SIGTERM

**位置**: `subscription_watch_background_runner.py:45`

runner 只注册了 `SIGTERM` -> `KeyboardInterrupt` 的转换。在 Linux 上，后台进程可能收到 `SIGHUP`（例如终端关闭），这不会被捕获。

**建议**: 对 `SIGHUP` 也注册相同的处理，或使用 `start_new_session=True`（已做）并确认不会收到意外的 SIGHUP。

---

## 设计文档与实现的差异汇总

| 设计文档声明 | 实际实现 | 差异程度 |
|---|---|---|
| `events.csv` 可选 | 始终写入 | 低 |
| status.json 字段集为文档所列 | task.py 额外注入了 artifacts、provider_instance_id 等字段 | 中 |
| Non-Goals: "不实现后台 daemon 化" | 已实现完整的后台 controller | 高* |
| Non-Goals: "不实现 start / stop / status / list 命令" | controller 已有 start / stop | 高* |

\* 注: 后台控制层已经实现但设计文档的 Non-Goals 仍写着不实现。这可能是设计文档未同步更新，或者后台控制被视为独立于"前台 run artifact contract"设计文档之外的增量。建议明确文档边界或更新 Non-Goals。

---

## 亮点

1. **reconcile 逻辑全面**: stale_process_state、malformed payload、mismatched pid 等边界情况都覆盖到了，且测试验证了持久化后的状态一致性。
2. **stop 信号降级链**: SIGTERM -> 等待 grace period -> SIGKILL -> 等待 force timeout，逻辑清晰且有测试覆盖。
3. **idempotency_key 设计**: 允许调用方安全重试 start 而不会产生副作用，这是后台任务控制的最佳实践。
4. **进程启动失败的双路径处理**: pid 写入失败时，如果能 terminate 则清理状态；如果不能 terminate 则保留 blocking state 防止新启动，这个设计很稳健。
5. **legacy 路径兼容**: 通过 `jsonl_output_path` / `csv_output_path` / `status_output_path` 参数保持向后兼容，不破坏现有 CLI 用法。

---

## 建议优先级

1. **立即修复**: P0 #1 (启动超时语义)、P0 #2 (schema version 不一致)
2. **落地前修复**: P0 #3 (stop 竞态)、P1 #4 (字段冗余)、P1 #8 (run_id 碰撞处理)
3. **后续迭代**: P1 #5-7 (manifest 补字段、函数命名、CSV 可选性)、P2 全部
