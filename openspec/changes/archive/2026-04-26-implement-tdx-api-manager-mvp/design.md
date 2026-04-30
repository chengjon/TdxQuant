## Context

当前仓库已经形成两条不同性质的能力链路：

- `tdxquant/desktop/` 为主的桌面自动化交易链路
- `tdxquant/api/bridge.py` 为主的 TdxQuant 查询接口桥接链路

问题不在于底层能力不存在，而在于查询能力的上层组织方式仍然过于扁平：

- 查询函数持续堆积在 `bridge.py`
- 查询命令持续堆积在 `cli.py`
- 日常使用时只能记忆大量扁平命令
- 尚未形成统一的代码调用门面
- 尚未形成可复用的 profile 驱动调用方式

本次变更只治理查询类 API 的顶层结构，不触碰现有桌面自动化交易实现，也不替换现有扁平 CLI。MVP 的目标是先形成一套可持续扩展的“bridge -> domain -> manager -> profile”骨架，再在后续阶段逐步纳入更多 capability。

## Goals / Non-Goals

**Goals:**
- 为查询类 TdxQuant 能力建立统一代码入口 `TdxApiManager`
- 将已接入的查询能力按业务域拆分为 `market` 与 `meta`
- 建立基于 JSON 配置文件的 API profile 机制
- 新增 `api` 二级 CLI 入口，降低日常使用成本
- 明确 MVP 阶段的边界，避免把写操作和交易能力混入新体系

**Non-Goals:**
- 不重构 `tdxquant/desktop/`、`tdxquant/brokers/` 与现有交易链路
- 不实现 `tqcenter` 长连接复用
- 不在本阶段引入 `formula.py`、`block.py`、`tasks/`
- 不把 `send_user_block` 和 formula 系列纳入 `TdxApiManager`
- 不废弃现有扁平 CLI 查询命令

## Decisions

### 1. 保留 `bridge.py` 作为底层透传层

`tdxquant/api/bridge.py` 已经承载统一错误封装、运行时初始化和结果序列化。MVP 阶段不拆空它，也不重写 `_run_tq_call` 的短连接模型。

理由：
- 现有底层行为已经稳定可用
- 如果同时重写底层连接模型，会把范围从“顶层治理”扩大为“底层重构”
- 审核意见已明确短连接模式应在 MVP 阶段保持现状

备选方案：
- 直接把连接复用下沉到 manager 或新 runtime 模块。短期收益低，风险高，因此放弃。

### 2. 将新的公共底座命名为 `context.py`

新增文件采用 `tdxquant/api/context.py`，而不是 `tdxquant/api/runtime.py`。

理由：
- 项目已存在 `tdxquant/runtime.py`，并被 `brokers/pingan.py` 引用
- 同名文件会显著增加 import、搜索和 IDE 跳转混淆
- `context.py` 更准确表达“顶层调用上下文与 profile 治理工具层”的职责

备选方案：
- `runtime.py`、`profile_helper.py`。前者冲突明显，后者过于偏向 profile，无法完整覆盖 timing 和 metadata 语义，因此不选。

### 3. domain 层保持无状态，profile 只在 manager 层合并

`market.py` 与 `meta.py` 只封装领域原子能力，不直接读取 profile 文件，也不调用 `context.py` 做 profile 合并。

理由：
- 保持依赖方向清晰：`manager -> context + domain -> bridge`
- 避免 domain 层承担过多顶层治理职责
- 更容易做参数透传测试和 mock 测试

备选方案：
- 每个 domain 自己解析 profile。会导致耦合和重复实现，因此不选。

### 4. `refresh_cache` 作为 manager 的直接方法

`refresh_cache` 在行为上属于运行时写动作，不适合放入只读语义的 `meta.py`。

理由：
- 审核意见已指出其归属 `meta` 语义牵强
- 将其暴露为 `manager.refresh_cache()` 更符合“少量运行时公共动作”的定位

备选方案：
- 放进 `meta.py`。会模糊只读查询边界，因此不选。

### 5. API profile 复用现有 profile override 风格，但改为 JSON 配置

API profile 的合并策略遵循现有 `pingan-buy` 模式：先取预设，再用显式传参覆盖；但配置存储从硬编码字典改为 `runtime/api-profiles.json`。

理由：
- 项目已有成熟的 `profile + override` 使用经验
- JSON 配置更适合后续扩展和日常维护
- 审核意见要求明确两者关系并避免设计风格分裂

备选方案：
- 保持硬编码字典。短期简单，但不利于长期维护，因此不选。

### 6. 新 `api` CLI 入口与旧扁平命令并存

MVP 新增 `api` 二级入口，但不删除、不隐藏现有 `tdx-data-*` 命令。

理由：
- 旧脚本和当前使用习惯不能被打断
- 新入口主要解决“日常使用成本高”的问题
- OpenSpec 与方案都要求兼容存量

备选方案：
- 直接切换到新入口。会破坏兼容性，因此不选。

### 7. CLI 二级命令继续使用 `argparse`，但抽独立处理函数

`cli.py` 保持现有技术栈，不引入新 CLI 框架；新增 `api` 二级 subparser，同时将执行逻辑抽离到独立函数中。

理由：
- 避免在 MVP 阶段引入额外依赖
- 可以控制 `main()` 分支继续膨胀
- 符合审核意见关于实现路径明确化的要求

备选方案：
- 重写 CLI 框架或继续把逻辑直接堆进 `main()`。前者范围过大，后者维护性差，因此都不选。

## Risks / Trade-offs

- [`cli.py` 继续变长] → 通过 `_build_api_parser()` / `_handle_api_subcommand()` 限制主流程膨胀。
- [`bridge.py` 仍然偏大] → MVP 阶段接受这一现实，只在其上建立 domain 层，后续再逐步拆分。
- [profile 默认值覆盖复杂参数行为不清] → 明确只允许 profile 提供默认值，显式参数优先。
- [新旧入口并存导致短期重复] → 这是兼容性成本，先接受，再逐步通过文档引导迁移。
- [`send_user_block` 与 formula 系列暂未纳入新体系] → 在工件和实现中显式声明暂留旧入口，避免错误预期。
- [配置文件路径依赖 CWD] → 由 `context.py` 统一用绝对路径解析，避免环境差异。

## Migration Plan

1. 新增 `context.py`，实现 profile 路径解析、profile 合并和 timing 工具。
2. 新增 `market.py`、`meta.py`，封装当前已接入的查询类 bridge 能力。
3. 新增 `manager.py`，聚合 domain 并暴露 `refresh_cache()`。
4. 新增 `runtime/api-profiles.json`，提供 MVP 预设。
5. 更新 `tdxquant/api/__init__.py`，导出 `TdxApiManager`。
6. 在 `cli.py` 中新增 `api` 二级入口，接入 manager。
7. 补充单元测试与 CLI 冒烟测试，验证新旧入口共存。

## Open Questions

- `api` 二级命令在后续阶段是否要进一步拆出单独 CLI 模块文件？
- 第二阶段引入 `task` 层时，是否直接复用 `TdxApiManager` 作为任务内部调用门面？
- `formula.py` 后续接入时，是作为 `manager.formula` 属性，还是单独的独立调用入口？
