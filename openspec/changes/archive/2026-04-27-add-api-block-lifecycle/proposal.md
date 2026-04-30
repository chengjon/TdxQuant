## Why

当前 query manager 的 `block` 子域只有 `send_user_block(...)`，而官方接口文档中的自定义板块生命周期能力还缺一个完整闭环：

- `get_user_sector`
- `create_sector`
- `delete_sector`
- `rename_sector`
- `clear_sector`

这组能力已经在覆盖矩阵中被明确标记为下一优先包。如果继续只保留 `send_user_block`，调用方仍然要么直接下沉到原始 `tqcenter`，要么在项目外自己拼板块管理逻辑，不符合当前“manager 层统一日常使用”的方向。

## What Changes

- 为 `block` 子域补齐自定义板块读写生命周期能力。
- 为 nested `api` 命令新增：
  - `user-sectors`
  - `create-sector`
  - `delete-sector`
  - `rename-sector`
  - `clear-sector`
- 为 flat bridge CLI 新增：
  - `tdx-get-user-sector`
  - `tdx-create-sector`
  - `tdx-delete-sector`
  - `tdx-rename-sector`
  - `tdx-clear-sector`
- 保持现有 `send_user_block` 入口兼容不变。
- 补充 parser、dispatch、domain delegation、manager metadata 测试，并更新覆盖文档。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-management`: 扩展 `block` 子域，使其提供自定义板块生命周期闭环。
- `tdx-api-cli-entry`: 扩展 nested `api` 与 flat bridge 查询/写入命令，使其支持自定义板块生命周期能力。

## Impact

- 影响 `tdxquant/api/bridge.py`、`tdxquant/api/block.py`、`tdxquant/api/manager.py` 与 `tdxquant/cli.py`。
- 影响 `tests/test_api_manager.py` 与 `tests/test_api_cli.py`。
- 影响 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与主 spec。
- 不影响 `meta` 域的只读边界，不影响 `runtime`、`task`、`report`、`catalog` 与桌面交易 capability。
