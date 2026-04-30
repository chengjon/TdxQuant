## Context

当前项目已经把几条最关键的 provider-facing contract 固定下来了：

- 通用同步 provider result envelope
- `formula.screen`
- `runtime.capabilities`
- `runtime.doctor`
- `block_mutation`
- provider-level subscription event row

但这些 contract 仍然缺一个正式的内置 sample/replay 层。现状是：

- 只有非常基础的 `provider_result_success / failure` 测试 fixture
- fixture 分散在测试侧，不适合作为对外可依赖资产
- 没有统一 loader 或 manifest

这会让上层项目继续各自维护样例，无法把 TdxQuant 当成“自带 contract fixtures 的 provider”。

## Goals / Non-Goals

**Goals:**

- 提供仓内稳定的 provider replay fixture bundle。
- 提供统一 manifest 和 loader helper。
- 同时覆盖同步 JSON contract 与异步 JSONL event contract。
- 为内部测试和外部上层项目提供同一份 fixture 基座。

**Non-Goals:**

- 不新增 HTTP replay 服务。
- 不新增 daemon 或 start/stop 控制面。
- 不把 live provider 调用自动切换成 replay mode。
- 不在本包里引入完整 fake runtime execution engine。

## Decisions

### 1. fixture 资产放进 `tdxquant/fixtures/provider`

fixture 将放在包内目录，而不是继续只放在 `tests/fixtures`。

理由：

- 上层项目需要稳定引用路径
- 这些 fixture 是 provider 产品资产，不只是测试私有文件
- 后续如果需要打包或复制给上层，也更自然

### 2. 统一通过 manifest + loader 暴露，而不是让调用方自行拼文件名

新增一个共享 helper 模块，至少提供：

- 列出内置 fixture catalog
- 根据名字定位 fixture 路径
- 自动加载 JSON 或 JSONL fixture

理由：

- 避免上层项目绑定目录结构细节
- 可以把格式、能力名、用途说明一起暴露出来
- 内部测试也能复用同一加载逻辑

### 3. 第一版 fixture bundle 只覆盖当前高价值 contract

第一版只覆盖当前对上层最有价值、且已稳定的能力：

- provider result success / failure
- `formula.screen`
- `runtime.capabilities`
- `runtime.doctor`
- `block_mutation`
- provider subscription event rows

理由：

- 先覆盖真正会被上层依赖的 contract
- 避免把所有能力一次性都做成样例资产，范围失控

### 4. fixture 以“样例 contract”定位，而不是“可执行 fake runtime”

本包不会把 fixture 接入 live runtime 调用链，只保证：

- 样例文件稳定
- loader 稳定
- contract test 可重复

理由：

- fake runtime 是单独复杂度层级
- 当前上层最急需的是稳定 sample 和 contract test 输入
- 保持本包小而可落地

## Risks / Trade-offs

- [fixture 样例可能与主 contract 漂移] → 用独立测试锁 manifest、格式和关键字段。
- [放在包内后会增加仓库资产量] → 第一版只保留高价值最小集合，不做大规模覆盖。
- [没有 live replay mode 可能让部分人觉得不够完整] → 文档明确第一版只解决 fixture distribution 与 contract test 基座。

## Migration Plan

1. 定义 provider replay fixtures spec。
2. 新增包内 fixture 目录与共享 loader。
3. 补 contract-oriented fixture 测试。
4. 更新对外文档与路线图。
5. 验证通过后归档。

## Open Questions

- 后续是否需要把其中一部分 fixture 再上提成 `runtime` discovery 可读 manifest，而不是只通过 Python helper 和文件路径提供。
