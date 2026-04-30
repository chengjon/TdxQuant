## Why

`trade buy` 和 `trade submit-once` 已经收敛到统一命名空间，但日常使用时仍需重复输入端口、窗口、profile 和延时参数。现在需要补一层可维护的交易 preset，把固定环境参数命名化，减少长命令改写成本。

## What Changes

- 为 `trade` 命令组增加可配置的 preset 机制。
- 新增 trade preset 列表入口。
- 新增 trade preset 执行入口，并把 preset 参数映射回既有 `trade buy` / `trade submit-once`。
- 增加独立的 runtime trade preset 配置文件。
- 保持现有 `trade buy` / `trade submit-once` 以及扁平 `pingan-buy*` 命令兼容。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-cli-entry`: 为既有 `trade` CLI 增加 preset 列表与 preset 执行能力

## Impact

- 影响 `tdxquant/cli.py`、trade runtime 配置解析、CLI 测试与交易使用文档。
- 不新增新的交易执行 manager，只扩展 CLI 入口层。
