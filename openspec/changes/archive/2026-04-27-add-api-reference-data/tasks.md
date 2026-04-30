## 1. Reference Data Tests

- [x] 1.1 为 `api divid-factors` 与 `api ipo-info` 补 parser 和 manager dispatch 测试。
- [x] 1.2 为 `meta` 域补 `divid_factors / ipo_info` delegation 与 manager metadata 测试。

## 2. Reference Data Implementation

- [x] 2.1 在 `bridge` 与 `meta` 域中新增 `divid_factors` 与 `ipo_info` 包装。
- [x] 2.2 在 `TdxApiManager.meta` 中暴露新的参考数据查询方法。
- [x] 2.3 在 CLI 中新增 nested `api` 子命令与对应 flat bridge 命令并完成分发。

## 3. Verification

- [x] 3.1 更新能力覆盖矩阵与相关 spec 中的参考数据说明。
- [x] 3.2 运行定向测试、语法校验与 OpenSpec 校验。
