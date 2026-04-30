## 1. API Domain Expansion

- [x] 1.1 梳理现有 formula 与 block 相关 bridge 能力，明确它们分别进入 `formula.py` 与 `block.py` 的归属边界。
- [x] 1.2 定义 `formula` domain 的原子方法范围，覆盖公式数据准备、单次执行与批量执行三类能力。
- [x] 1.3 定义 `block` domain 的原子方法范围，优先覆盖 `send_user_block` 并明确其写操作边界。
- [x] 1.4 设计 `TdxApiManager` 的四域结构：`market`、`meta`、`formula`、`block`。

## 2. CLI Expansion

- [x] 2.1 规划 `api` 二级命令如何逐步承接 formula 能力，同时保留现有扁平公式命令兼容。
- [x] 2.2 规划 `api` 二级命令如何承接 block 能力，同时保留 `tdx-send-user-block` 兼容。

## 3. Task Layer Planning

- [x] 3.1 定义 task 层与 manager 层的边界，明确 task 只做场景编排、不直接调用 `bridge.py`。
- [x] 3.2 规划首批稳定 task 场景，至少覆盖板块研究、公式扫描、自选刷新或环境运维中的若干项。
- [x] 3.3 规划 task profile 方案，明确其与 `api-profiles.json` 的分工关系。
- [x] 3.4 规划未来 `task` 二级 CLI 入口的定位与兼容策略。

## 4. Delivery Boundaries

- [x] 4.1 明确本次 change 只做 API 侧第二阶段规划，不涉及桌面自动化交易 capability。
- [x] 4.2 列出后续建议的实现顺序：先 domain/manager，再 CLI，最后 task 层落地。
