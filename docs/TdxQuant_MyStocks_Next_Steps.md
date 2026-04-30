# TdxQuant 面向 MyStocks 的下一步开发与改进方向

本文基于以下材料整理：

- [TdxQuant_Project_Function_Map.md](/opt/iflow/TdxQuant/docs/TdxQuant_Project_Function_Map.md)
- [TdxQuant_Integration_Questions.md](/opt/iflow/TdxQuant/docs/TdxQuant_Integration_Questions.md)
- `/opt/claude/mystocks_spec/docs/reports/analysis/TDXQUANT_INTEGRATION_QUESTIONS_RESPONSE_MYSTOCKS_2026-04-28.md`

本文只代表“根据 MyStocks 反馈，TdxQuant 本项目下一步该如何开发/改进”的结论，不代表另一个上层项目 `quantix` 的最终约束。

## 1. 核心结论

MyStocks 已经给出了比较明确的接入立场：

- 认可 TdxQuant 的接入价值。
- 希望将 TdxQuant 定位为 `TongDaXin 特定能力 provider`。
- 希望以 `Windows sidecar / provider` 方式接入，而不是作为 Linux/WSL 主进程内嵌库。
- 希望优先接入：
  - `formula`
  - `market / meta / financial / transaction`
  - `realtime subscription`
  - `block sync`
- 不希望早期把 `send_warn` 和桌面自动化交易放进主接入路径。
- 接受 `query path` 与 `trade path` 完全分离。

这意味着，本项目下一步的重点不应是继续泛化新功能，而应转向“把现有能力整理成一个可被上层系统稳定消费的 Windows provider”。

## 2. 对本项目的直接影响

MyStocks 的反馈把本项目后续方向收敛成了 5 个核心要求：

### 2.1 要从“可用工具”升级为“可集成 provider”

当前项目已经有较完整的 manager / task / trade 能力，但从 MyStocks 的视角看，真正缺的不是更多原子函数，而是：

- 稳定的 machine-readable 协议
- 稳定的 capability 边界
- 稳定的 Windows provider 运行模型

### 2.2 要优先产品化查询、公式、订阅和板块

MyStocks 要的不是全量接入，而是分阶段接入：

1. 只读能力
2. 实时订阅
3. 板块同步
4. 交易实验线

因此，本项目的优先级也应跟着调整，而不是把 query、trade、catalog 等各条线平均推进。

### 2.3 要明确区分“同步结果协议”和“事件流协议”

MyStocks 已明确偏好：

- 同步调用：`JSON`
- 实时事件：`JSONL`，其次 `SSE`
- `CSV`：只作为导出 artifact

这要求本项目把“结果输出”正式视为契约，而不是命令行附带产物。

### 2.4 要尽快提供健康探测能力

MyStocks 明确将 `capability doctor / runtime doctor / health probe` 视为高优先级需求。

这意味着本项目不能只在失败时返回 `unsupported_platform` 或运行时错误，而要能在调用前说明：

- 当前平台是否支持
- TongDaXin 是否启动
- `TPythClient.dll` 是否可用
- 实时订阅是否可用
- 当前 provider 暴露了哪些 capability

### 2.5 高风险写入和交易能力必须后置

MyStocks 已明确：

- `send_warn` 不应早期进入主接入路径
- 桌面自动化交易只能进入 `experimental / manual-confirmed / broker-specific`

因此，本项目需要把“可集成主线能力”和“实验高风险能力”分层治理。

## 3. 下一步开发方向

建议将下一步工作拆成以下 6 个方向。

### 方向 A：固定同步结果协议

这是第一优先级。

目标：

- 固定统一 `JSON` 结果包络
- 固定错误码
- 固定 `data` 字段结构约定
- 固定 timing metadata
- 固定 artifact path 命名
- 引入 `capability_version`
- 引入 `schema_version`

建议统一的基础字段至少包括：

- `success`
- `code`
- `message`
- `capability`
- `capability_version`
- `schema_version`
- `runtime`
- `profile`
- `session_id`
- `started_at`
- `elapsed_ms`
- `data`
- `artifacts`

这一步完成后，本项目才能被稳定当作 `CLI + JSON` 或 `service + JSON` provider。

### 方向 B：建设 Windows provider 健康探测面

这是与方向 A 并列的高优先级。

目标：

- 提供统一的 `capability doctor / runtime doctor / health probe`
- 明确列出当前 provider 的可用 capability
- 将平台、TongDaXin、DLL、订阅 runtime、窗口/HID 能力全部纳入探测

建议最少覆盖：

- `platform_supported`
- `tdx_process_up`
- `tpython_client_available`
- `query_runtime_ready`
- `subscription_runtime_ready`
- `window_probe_ready`
- `hid_ready`
- `trade_runtime_ready`
- `capabilities`

输出必须是稳定 JSON，而不是仅供人工阅读的文本。

### 方向 C：把订阅能力正式产品化

这会是 MyStocks 真正用到的第一批动态能力。

目标：

- 在现有 `open_subscription_session()` 之上，建设稳定的前台或常驻入口
- 优先形成 `subscription-watch` 任务或 worker
- 产出标准 `JSONL` 事件流
- 提供 session 状态与 reconnect metadata
- 支持优雅退出
- 提供状态文件

建议从以下能力开始：

- `task subscription-watch`
- `status` 文件
- `events.jsonl`
- `summary.json`

后续再评估是否增加：

- `SSE` 输出
- `stop / status / list`
- Redis 内部桥接

### 方向 D：加强 query/formula 的 provider-ready 质量

这部分不是补函数覆盖，而是做“上层可稳定消费”的治理。

目标：

- 复核 `formula / market / meta / financial / transaction` 这些已实现能力的输出一致性
- 补齐批量调用下的 metadata
- 明确 capability 命名
- 明确字段稳定性
- 保证 `elapsed_ms` 一致可用

重点不是再加很多新命令，而是让现有命令真正适合作为外部集成面。

### 方向 E：为板块同步补写入安全治理

MyStocks 接受板块写能力，但要求它晚于只读能力，并且必须有写入治理。

目标：

- 为 `send_user_block` 以及板块生命周期写操作补齐审计与失败反馈
- 增加幂等或重复写保护
- 区分读能力与写能力的接入级别

建议补齐：

- write audit log
- mutation result schema
- failure reason
- idempotency strategy

这样后续才适合做：

- MyStocks watchlist -> TongDaXin block
- TongDaXin block -> MyStocks watchlist

### 方向 F：继续隔离交易主线，并补风险治理

这部分不是当前主线，但必须继续补边界。

目标：

- 在文档、目录、配置、输出协议上继续强化 `query path` 与 `trade path` 分离
- 明确桌面交易只处于 `experimental` 路径
- 逐步补交易安全治理

如果未来需要进入上层系统，至少要先具备：

- `idempotent submission key`
- `pre-trade risk gate`
- 二次确认策略
- durable audit log
- broker/runtime health check

在这些条件满足前，交易线不应作为 MyStocks 主接入能力推进。

## 4. 建议的开发顺序

基于 MyStocks 的反馈，建议本项目按以下顺序推进：

### 第 1 阶段：Provider 基础治理

- 固定 JSON 结果协议
- 固定错误码与版本字段
- 补 capability doctor / runtime doctor / health probe
- 强化 query path / trade path 边界文档

### 第 2 阶段：只读能力 provider-ready

- 统一 `formula / market / meta / financial / transaction` 输出
- 补批量调用 metadata
- 验证 Windows provider 下的可用性与稳定性

### 第 3 阶段：订阅产品化

- 推出 `subscription-watch`
- 固定 JSONL 事件包络
- 提供 session 状态、状态文件与恢复信息

### 第 4 阶段：板块同步准备

- 补 block 写入审计
- 补失败反馈
- 补幂等或重复写保护

### 第 5 阶段：交易线单独治理

- 仅保留在 `experimental`
- 继续做风险控制、审计和健康检查
- 不纳入当前对 MyStocks 的主线集成目标

## 5. 不建议当前优先推进的内容

基于 MyStocks 的立场，以下内容不应作为当前第一优先级：

- 把 TdxQuant 做成 Linux/WSL 主进程内嵌库
- 让 Python import 成为唯一正式集成面
- 先做桌面交易集成
- 让 `send_warn` 进入早期主接入路径
- 让 `catalog` 或 `task` 反向主导上层系统架构
- 继续在未固定协议前扩太多新入口

## 6. 推荐的后续文档 / OpenSpec 工作包

为便于真正落地，建议后续将工作拆成独立 change，而不是混成一个大包。

建议候选方向：

1. `provider-result-contract`
   - 统一 JSON 包络、错误码、schema version、capability version
2. `provider-health-doctor`
   - 平台、TongDaXin、DLL、subscription、window/HID 探测
3. `task-runtime-subscription-watch`
   - JSONL 事件流、状态文件、session 管理
4. `block-mutation-safety`
   - 审计、失败反馈、幂等/重复写防护
5. `trade-safety-hardening`
   - 仅面向实验交易线的风险治理补强

这些名字只是建议，重点是按能力边界拆小，而不是一次性推进。

## 7. 一句话总结

根据 MyStocks 的反馈，本项目下一步最重要的事情不是“继续补更多 TongDaXin 函数”，而是把现有能力收口成一个：

- 运行在 Windows 侧
- 协议稳定
- 可健康探测
- 可输出标准 JSON / JSONL
- 查询主线与交易主线清晰分离

的 TongDaXin provider。
