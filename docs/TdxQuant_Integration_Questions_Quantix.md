# TdxQuant 面向 quantix-rust 的集成问题清单

本文用于和 `quantix-rust` 沟通 `TdxQuant` 的定向集成问题。

它不是 [TdxQuant_Integration_Questions.md](/opt/iflow/TdxQuant/docs/TdxQuant_Integration_Questions.md) 的简单复制版，而是基于 `quantix-rust` 当前评估结论做的收敛版，重点关注：

- Rust / Windows bridge 边界
- 稳定机器协议
- 窄范围 PoC
- 订阅长期契约
- capability 分级
- contract test / replay

## 1. 这份问卷的前提

根据 `quantix-rust` 当前评估，以下几点已经基本明确，不需要再作为开放性问题反复讨论：

- `TdxQuant` 值得接，但应选择性接入。
- 最值得接的是：
  - `formula`
  - `block`
  - `subscription`
- 不建议当前直接接入：
  - `desktop trade`
  - 让 `TdxQuant` 进入主执行链路
- 不建议直接库级嵌入 / FFI / PyO3 深耦合。
- 更适合的方式是：
  - `Windows provider`
  - `bridge boundary`
  - `HTTP + JSON / JSONL` 或 `CLI + JSON / JSONL`

因此，这份问卷主要不是问“要不要接”，而是问：

- 先接哪一条
- 用什么协议接
- 契约怎么固定
- 生命周期谁负责

## 2. 首先要确认的集成面

### 2.1 Phase 1 你更希望先验证哪种接入面

候选通常只有两种：

- `Bridge HTTP + JSON/JSONL`
- `CLI + JSON/JSONL`

需要确认：

- `quantix-rust` 第一阶段更偏向哪种
- 另一种是否只作为备选或过渡
- 长期正式集成面是否仍然优先 `service-first`

### 2.2 Windows provider 的所有权归谁

需要确认：

- 是希望 `TdxQuant` 自己逐步长成 provider
- 还是希望 `quantix-rust` 现有 Windows bridge 包一层，把 `TdxQuant` 作为内部能力源

这个问题会直接影响：

- 健康检查入口放在哪里
- 能力发现入口放在哪里
- session 生命周期由谁管理
- 协议契约由谁固定

## 3. 建议优先验证的 PoC

### 3.1 你更希望先做哪条窄 PoC

当前最自然的 3 条候选是：

1. `公式选股 -> 标准股票列表 -> quantix watchlist`
2. `公式选股 -> 标准股票列表 -> TongDaXin block`
3. `subscription-watch -> JSONL -> quantix monitor`

需要确认：

- 第一阶段只选哪一条或两条
- 哪条最能证明“接入是值得的”
- 哪条最容易做出稳定 contract test

### 3.2 PoC 的成功标准是什么

建议明确：

- 输出是否稳定可解析
- 是否能重复运行
- 是否能脱离真实交易环境复验
- 是否能进入 `watchlist / monitor / strategy` 的下游链路
- 是否能被 bridge/contract test 稳定验证

如果成功标准不先定死，PoC 很容易从“验证架构”变成“扩功能”。

## 4. 同步机器协议

`quantix-rust` 比 `mystocks` 更依赖清晰的机器协议，因此这部分需要问得更细。

### 4.1 同步结果 JSON 包络

需要确认 `quantix-rust` 希望固定哪些字段。

建议至少明确：

- `success`
- `code`
- `message`
- `capability`
- `capability_version`
- `schema_version`
- `runtime`
- `started_at`
- `elapsed_ms`
- `data`
- `artifacts`

### 4.2 字段与格式规范

需要确认：

- 时间格式是否统一为 `RFC3339`
- 证券代码格式是否固定为字符串
- 市场、复权、周期等枚举是否要固定字面值
- 退出码是否需要形成稳定 contract
- 批量返回时的 `data` 结构希望是数组、映射还是 envelope 嵌套

这部分如果不先固定，Rust 侧很难建立长期稳定的数据模型。

## 5. 订阅事件契约

`quantix-rust` 明显更关心“可长期运行的订阅任务”，而不是单纯的 `subscribe_hq()` 函数。

### 5.1 事件包络需要固定到什么程度

建议确认是否需要从一开始就固定：

- `session_id`
- `subscription_id`
- `sequence`
- `event_type`
- `symbol`
- `source_ts`
- `event_ts`
- `schema_version`
- `payload`
- `provider_instance_id`
- `reconnect_metadata`

### 5.2 订阅生命周期语义

需要确认是否需要稳定提供：

- `start`
- `stop`
- `status`
- `list`
- 优雅退出
- session 恢复语义
- 丢事件后的告警语义
- 背压 / 缓冲语义

如果这些是刚需，那 `subscription-watch` 就不能只停留在“能跑起来”，而要从第一版就带有 provider contract 的意识。

## 6. 能力层与入口层边界

`quantix-rust` 的一个重要关切是：不要让上层被 `task / report / catalog` 的入口层结构绑死。

需要确认：

- `quantix-rust` 希望依赖的是能力层 contract，还是入口层 contract
- 是否接受：
  - `formula / block / subscription` 作为一等 capability
  - `task / report / catalog` 只作为人类操作入口
- 是否希望完全避免把 `preset / bundle / catalog layout` 暴露成正式集成面

这会直接影响本项目后续如何定义“稳定能力”与“便利入口”。

## 7. capability 发现与 capability 分级

这是 `quantix-rust` 评估中比通用问卷更突出的点。

### 7.1 需要发现哪些能力

建议确认 `quantix-rust` 是否希望 provider 能明确声明：

- 当前可用 capability 列表
- capability 的稳定级别
- capability 的运行前提
- capability 当前是否 degraded

### 7.2 是否需要 capability 分级

建议确认是否要从一开始就把能力分成至少 3 类：

- 只读能力
- 会改本地客户端状态的能力
- 会触发实盘副作用的能力

如果接受，这个分级应当进入：

- 文档
- health probe
- 能力发现输出
- 风险控制逻辑

## 8. contract test / replay / 假数据模式

这是 `quantix-rust` 提出的一个很有价值的特殊要求。

需要确认是否希望 `TdxQuant` 提供：

- 固定样例输入
- 固定 JSON 输出样例
- 事件流样例
- replay 模式
- 假数据 / 假 provider 模式
- contract test 夹具

还需要确认这些夹具主要服务于哪一层：

- Rust bridge contract test
- provider 自测
- 端到端集成测试

如果这块需求强，本项目后续就不该只做“真实环境可跑”，还要做“脱离真实客户端也可复验”。

## 9. 性能与批量场景

`quantix-rust` 不一定需要 TdxQuant 接管基础行情，但如果接入公式、订阅、板块，就会关心批量和吞吐。

需要确认：

- 批量公式计算是否是第一阶段核心场景
- 批量板块写入的规模级别
- 长驻订阅对事件延迟的可接受范围
- 是否需要 provider 输出 session 级运行统计
- 是否需要缓存或复用长驻 session

## 10. 责任边界

需要和 `quantix-rust` 再确认一遍哪些边界已经锁死。

建议明确：

- `TdxQuant` 负责：
  - TongDaXin 特有能力
  - 公式能力
  - 板块能力
  - 订阅任务与事件输出
- `quantix-rust` 负责：
  - 执行内核
  - 风控
  - 状态所有权
  - monitor / watchlist / strategy 的上层业务语义

还需要确认是否明确不接受：

- `desktop trade` 进入主执行链路
- `catalog/report` 反向主导 `quantix-rust` 入口结构
- 直接库级深耦合

## 11. 建议 quantix-rust 优先给出的信息

如果不想一次回答太多，建议至少先确认以下 8 项：

1. 第一阶段更偏 `Bridge HTTP` 还是 `CLI + JSON/JSONL`。
2. Windows provider 的所有权更希望放在谁那里。
3. 第一条 PoC 选哪条。
4. PoC 的成功标准是什么。
5. 同步 JSON 包络需要固定哪些字段和格式。
6. 订阅事件包络是否需要 `sequence / source_ts / reconnect_metadata`。
7. 是否需要 capability 分级与 capability 发现机制。
8. 是否需要 contract test / replay / 假数据模式。

## 12. 建议的回复模板

建议 `quantix-rust` 按下面模板回复：

```md
## 项目名称

### Phase 1 首选接入面

### Windows provider 所有权

### 第一条 PoC

### PoC 成功标准

### 同步 JSON contract 要求

### 订阅 JSONL contract 要求

### capability 发现 / capability 分级要求

### replay / contract test 要求

### 性能与批量要求

### 明确不接受的集成方式
```

## 13. 一句话总结

给 `quantix-rust` 的问题，不应再以“是否认可 Windows provider”这类通用问题为主，而应转向：

- 先用什么协议
- 先做哪条 PoC
- 机器契约如何固定
- 生命周期和所有权怎么划
- 如何让 Rust 侧能稳定复验和升级
