## Context

`subscription-watch` 在实现前已经具备前台订阅运行能力，但它的 artifacts 还停留在“导出文件”层面：调用方知道有 JSONL、CSV 和状态文件，却不知道哪一个是正式 contract，也没有稳定的 run 目录、manifest 或 replay fixture 约束。与此同时，项目已经先后收紧了同步 provider result envelope、capability discovery payload 和 built-in replay fixtures，订阅线继续保持临时约定会让整体 provider contract 出现一块明显短板。

实现已经落地在 `ff49d87`，因此本次设计是一次 retroactive spec closure：把已经实现并验证的行为补成正式 OpenSpec change，然后同步回主 spec 与 archive。

## Goals / Non-Goals

**Goals:**
- 把 `subscription-watch` 定义为一次独立 `run`，每次执行创建新的 `run_id` 目录。
- 固定 `events.jsonl`、`status.json`、`summary.json`、`manifest.json` 的 contract 和职责边界。
- 扩展 subscription event row，让 run 级元数据成为 provider-level contract 的一部分。
- 将 `subscription-watch` run artifacts 纳入 built-in replay fixture catalog。
- 保留既有 CLI 参数和 CSV 导出能力，但把它们降级为兼容投影。

**Non-Goals:**
- 不引入后台 daemon、`start/stop/status/list` 命令或跨 run 聚合视图。
- 不变更 `subscription-watch` 的核心运行方式，仍然维持前台 session 驱动模型。
- 不把 stdout 事件流升级为正式 machine contract。

## Decisions

### 1. `subscription-watch` 采用独立 run 目录模型

每次 `manager.subscription_watch(...)` 执行都创建新的 `run_id` 目录，canonical files 固定写入该目录。这样可以把一次运行的全部 machine-readable state 收口成单一 artifact bundle，而不是让调用方在 export paths 和终端输出之间拼装状态。

未采用“固定目录续写”的原因是它会把不同运行混在一起，削弱 replay、对账和失败排查的确定性。

### 2. `events.jsonl` 是唯一 canonical 事件 contract

事件 contract 以 JSONL 为主线，CSV 只保留为兼容投影。实现上通过统一 append path，把 JSONL 视为唯一事实源，再从同一批 normalized rows 投影到 CSV 和 legacy custom paths。

未采用“双主线 contract”的原因是 stdout/CSV 同时作为正式协议会让 payload 漂移面翻倍，并使 replay fixture 无法收敛到单一格式。

### 3. 新增专用 helper 模块负责 run artifact contract

`tdxquant/subscription_watch_run.py` 负责 `run_id`、canonical paths 和 manifest/status/summary builders；`tdxquant/subscription_event.py` 继续只负责 event row normalization；`tdxquant/api/task.py` 只负责 orchestration 与写盘。

这样做比继续把所有 artifact payload 拼装塞在 `api/task.py` 里更稳，原因是 run metadata 和 event metadata 的边界会更清晰，后续扩 replay/fake provider 时也有可复用的 builder。

### 4. Built-in replay fixtures 同步收口 `subscription-watch` run artifacts

除了升级 `subscription-event-batch.jsonl`，还新增 `subscription-watch-events`、`subscription-watch-status-completed`、`subscription-watch-summary-completed` 和 `subscription-watch-manifest` fixture 样例，并在 registry 中稳定注册。

未采用“只保留 event batch fixture”的原因是这会让上层仍然看不到 run artifact contract 的完整面，尤其是 `summary.json` 和 `manifest.json` 的字段约束无法被 loader 和 tests 锁定。

## Risks / Trade-offs

- [兼容路径增多] → 通过把 legacy output path 明确降级为镜像写出，避免它们继续定义主 contract。
- [状态文件与总结文件可能在中断场景不一致] → 通过统一 builder 和 finally-path 写出 `summary.json`，并用 keyboard interrupt tests 锁住 `final_state` / `stop_reason`。
- [现有代码集中在 `api/task.py`，改动容易影响无关任务] → 将 run artifact builder 提取到独立模块，并用 targeted tests 仅覆盖 `subscription-watch` 路径。

## Migration Plan

1. 保留 `task subscription-watch` 入口和已有参数不变。
2. 让默认输出改为写入 `runtime/subscription-watch/<run_id>/`。
3. 对显式 `jsonl_output_path` / `csv_output_path` / `status_output_path` 继续兼容，但它们只作为镜像文件。
4. 用 replay fixtures、manager tests 和 targeted CLI tests 固定新 contract。
5. 将 delta specs 同步回主 spec 后 archive 本 change。

## Open Questions

None. 该 change 对应的实现和验证已经完成，本次 design 不保留待决项。
