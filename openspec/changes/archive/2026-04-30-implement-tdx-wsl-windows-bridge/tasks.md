## 1. Bridge Foundation

- [x] 1.1 设计并实现通达信专用 bridge 命令分组，统一区分数据、公式、交易和健康检查入口。
- [x] 1.2 定义统一 JSON 返回结构和错误码映射，保证 WSL 侧无需解析纯文本。
- [x] 1.3 增加 Windows 运行前置检查，覆盖 Python 平台、TdxQuant 运行状态、通达信主窗口和 HID 串口可用性。

## 2. Data API Bridge

- [x] 2.1 在 Windows 端探测并验证 TdxQuant 官方 Python 接口可用性，输出最小健康检查结果。
- [x] 2.2 实现快照桥接命令，优先覆盖 `get_market_snapshot` 及字段过滤。
- [x] 2.3 实现 K 线桥接命令，覆盖有效参数校验和结构化 JSON 返回。
- [x] 2.4 实现标的信息与板块列表桥接命令，至少覆盖 `get_stock_info`、`get_sector_list`、`get_stock_list_in_sector`。

## 3. Formula Bridge

- [x] 3.1 实现指标公式桥接命令，优先覆盖 `formula_zb`。
- [x] 3.2 实现条件选股和专家公式桥接命令，优先覆盖 `formula_xg` 和 `formula_exp`。
- [x] 3.3 实现批量公式桥接命令，覆盖 `formula_process_mul_zb` 和 `formula_process_mul_xg`。
- [x] 3.4 实现公式数据准备命令，覆盖 `formula_set_data`、`formula_set_data_info`、`formula_get_data`。

## 4. Trading / HID Bridge

- [x] 4.1 将现有通达信探测命令整理为 bridge 能力，统一输出买入页句柄和证据。
- [x] 4.2 保留并整理现有 HID 协议客户端能力，支持 `PING`、`KEY`、`TYPE` 等最小命令集。
- [x] 4.3 把 `tdx-hid-buy-probe` 纳入统一 bridge 入口，复用前台校验、HID 输入、Win32 填价填量和弹窗抓取。
- [x] 4.4 在真实通达信环境下验证 HID 输入是否能把提示从“请输入证券代码!”推进到真实确认流程。
  按范围调整关闭说明：`2026-04-30` 的原生 Windows 实机验证确认当前 `TongDaXin V7.73` 账户在本机环境下 `F12 -> 无权限`，交易页不可达；同时项目方向已调整为“后续交易执行主线采用 PingAN + HID，暂时关闭 TongDaXin 交易线”。因此该项不再继续追踪为待恢复验证任务。

## 5. Documentation and Recovery

- [x] 5.1 更新 README，明确这条分支的主目标是“WSL <-> Windows TDX bridge”，不再只围绕平安证券和零散 Win32 命令。
- [x] 5.2 补一份通达信 bridge 开发文档，明确推荐的第一批命令、调用方式和运行边界。
- [x] 5.3 记录文档源质量限制，标明接口说明文档可作为实现依据，而转换质量差的红宝书文档暂不直接作为开发依据。
