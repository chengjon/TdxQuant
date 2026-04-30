## 1. Block Surface Tests

- [x] 1.1 为 `api user-sectors / create-sector / delete-sector / rename-sector / clear-sector` 补 parser 与 manager dispatch 测试。
- [x] 1.2 为 `block` 域补 lifecycle delegation 与 manager metadata 测试。

## 2. Block Surface Implementation

- [x] 2.1 在 `bridge` 与 `block` 域模块中新增 `get_user_sector`、`create_sector`、`delete_sector`、`rename_sector`、`clear_sector` 包装。
- [x] 2.2 在 `TdxApiManager.block` 中暴露新的板块生命周期方法，并保持 `send_user_block` 兼容。
- [x] 2.3 在 CLI 中新增 nested `api` 子命令与对应 flat bridge 命令并完成分发。

## 3. Verification

- [x] 3.1 更新能力覆盖矩阵与相关 spec 中的 block 生命周期说明。
- [x] 3.2 运行定向测试、语法校验与 OpenSpec 校验。
