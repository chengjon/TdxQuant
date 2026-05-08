# Task Block Read Full Preset Design

Date: 2026-05-05

## Terminology

- **Preset**
  - 指 `runtime/task-presets.json` 中的完整条目，包含：
    - `command`
    - `description`
    - `profile`
    - `options`
- **Profile**
  - 指 preset 条目中的 `profile` 字段值，或 `TASK_COMMAND_DEFAULT_PROFILES` 为某个 command 提供的默认 profile 名
- **`TASK_COMMAND_DEFAULT_PROFILES`**
  - 指 `tdxquant/tasking.py` 中的 command -> default profile 映射表

第一版 `task-block-read-full-preset` 只是在现有 preset 体系里新增一个允许目标命令，并不引入新的 profile 概念或第二套 preset 数据模型。

## Context

`task block-read-full` 已经落地为稳定的高层读侧 diagnostics task，解决了：

- provider-level `block.read_watchlist_snapshot(...)`
- task-level `data.read_full` diagnostics summary
- 独立 CLI 入口：
  - `tdxquant task block-read-full --block-code ZXG`

但它还不能像 `block-read-watchlist-export` 一样，通过现有 task preset 体系复用固定的日常参数。当前缺的不是新的 preset 机制，而是把这条新 task 接进已经存在的：

- `runtime/task-presets.json`
- `resolve_task_preset(...)`
- `task run --preset ...`

第一版只解决一件事：

- 让 `block-read-full` 成为现有 `task run --preset ...` 的合法目标命令

## Goals

- 把 `block-read-full` 接入现有 task preset 体系
- 继续复用：
  - `runtime/task-presets.json`
  - `resolve_task_preset(...)`
  - `task run --preset ...`
- 第一版 preset 只支持静态默认值：
  - `block_code`
- 显式 CLI `--block-code` 继续覆盖 preset 默认值

## Non-Goals

- 不修改 task preset schema
- 不支持模板变量或路径占位符
- 不支持运行时插值
- 不新增 catalog entry
- 不新增 provider capability
- 不新增导出、report、写回或后台控制语义
- 不把 `block-read-full` 接进 `TASK_COMMAND_DEFAULT_PROFILES` 之外的第二套 preset 路径

## Recommended Approach

采用最小接入方案：

- 只把 `block-read-full` 加入 task preset allowlist
- 继续复用现有 task preset 合并与 dispatch 逻辑
- 不为它单独发明第二套 preset 解析路径
- 第一版总体仍按最小接入推进；唯一一起补上的小幅 hardening，是对缺少 `block_code` 的 preset 做显式早失败，避免把错误延后到更深层 dispatch

原因：

- 当前缺口不是“preset 系统不够强”，而是“新 task 尚未成为 preset 合法目标”
- 这样最稳，也最符合现有 task preset 的职责

## Preset Contract

第一版 preset 条目继续沿用当前 task preset 结构，例如：

```json
{
  "read-zxg-full": {
    "command": "block-read-full",
    "description": "Read full diagnostics view for ZXG.",
    "profile": "default",
    "options": {
      "block_code": "ZXG"
    }
  }
}
```

关键约束：

- `command` 必须是：
  - `block-read-full`
- `options` 第一版只允许静态默认值：
  - `block_code`

不支持：

- `output`
- `export_output`
- `overwrite`
- 模板变量
- 路径插值
- 写回参数

这里需要强调：

- 现有 task preset schema 仍允许顶层 `profile` / `api_profile`
- 但这条 change 不扩 `block-read-full` 的 task-specific 参数面
- 第一版真正新增/消费的 task-specific preset 值只有：
  - `options.block_code`
- `options` 里的 key 还必须与 argparse namespace 中的目标字段名**精确一致**
  - 这里依赖的是：
    - preset `options.block_code`
    - CLI `--block-code`
    - argparse `dest=block_code`
  - 如果命名不一致，现有 generic merge 不会做语义映射

## CLI Semantics

### Listing

`task presets` 应能够列出指向 `block-read-full` 的 preset。

### Execution

`task run --preset read-zxg-full` 最终仍然应 dispatch 到：

- `TdxTaskManager.block_read_full(...)`

而不是新增一条 preset 专用执行路径。

### Override Rules

显式 CLI 参数必须继续覆盖 preset 默认值。

例如：

```bash
python -m tdxquant.cli task run \
  --preset read-zxg-full \
  --block-code MYZXG
```

最终调用应以显式 CLI 参数为准：

- `block_code="MYZXG"`

而不是 preset 中的默认 `ZXG`。

### `--output` boundary

`block-read-full` 继续复用 `_add_task_common_arguments(...)`，因此通用 `--output` 仍存在；它只表示“把整条 JSON result 写到文件”，不是这条 preset 线的领域参数，也不需要新增 `output` / `export_output` 选项。

## Implementation Surface

这条线我建议只动 4 个面。

在进入具体文件前，先把相关函数的覆盖边界定清：

| 函数 / 常量 | 改动? | 原因 |
|---|---|---|
| `TASK_COMMAND_DEFAULT_PROFILES` | yes | 新增 `"block-read-full": "default"` 以把它纳入 preset allowlist |
| `resolve_task_preset(...)` | no | 现有职责只是 load + normalize + override merge，不需要为这条命令新增特殊逻辑 |
| `_build_task_preset_namespace(...)` | yes | 只补 `block-read-full` 缺少 `block_code` 的显式早失败，避免把配置错误延后到更深层 dispatch |
| `_handle_task_subcommand(...)` | no | `block-read-full` 的 dispatch 分支已经存在，只需让 preset 合并后的 namespace 正确到达它 |

### 1. `tdxquant/tasking.py`

更新 `TASK_COMMAND_DEFAULT_PROFILES`，把：

- `block-read-full`

加入现有 task preset 支持命令集合。

默认 profile 建议固定为：

- `"default"`

这是向后兼容的最小增量：

- `TASK_COMMAND_DEFAULT_PROFILES` 当前是普通 dict lookup
- 只追加一个新 key，不会改变已有 preset 的解析或 dispatch 路径
- 已存在的 preset command 行为不应受影响

### 2. `tdxquant/cli.py`

复用现有 `_build_task_preset_namespace(...)` 和 `_handle_task_subcommand(...)` 逻辑，不新开分支模型。

需要确保：

- preset 解析后能把 `task_command` 设置为 `block-read-full`
- preset `options.block_code` 能正确映射到 dispatch 读取的 `args.block_code`
- `task run --preset ... --block-code ...` 能覆盖 preset 默认值
- `block-read-full` preset 若缺少 `block_code`，必须在 preset execution 阶段稳定失败
- 最终复用现有 dispatch：
  - `manager.block_read_full(...)`

这里要明确：

- `block-read-full` 的独立 dispatch 分支已经存在
- 因此本包 CLI 的重点不是新增 dispatch 分支，而是让 preset 合并后的 namespace 正确到达这个已有分支
- `resolve_task_preset(...)` 本身无需改动；本包新增的最小 hardening 只落在 `_build_task_preset_namespace(...)`
- 对 `block_code` 之外额外 `options` key 的严格拒绝不作为第一版必需项；如果后续要做更强 schema 校验，应单独开 follow-up

### 3. `runtime/task-presets.json`

新增至少一个 representative preset 示例，固定：

- `block_code`

目的不是提供最终业务模板全集，而是确保：

- 这条命令能真实进入 task preset 体系
- 列表和运行路径都有真实样例

### 4. Tests

focused tests 只补 preset 这条链：

- `task presets` 列表中能出现该命令
- `task run --preset ...` 能正确 dispatch 到 `manager.block_read_full(...)`
- CLI 显式 `--block-code` 能覆盖 preset 默认值
- preset target 若不在 allowlist 中，继续按当前 invalid-request 语义失败
- 如果 preset 缺少 `block_code`，应在 `_build_task_preset_namespace(...)` 阶段稳定失败，而不是等到更深层 dispatch 再报不明确错误

## Testing

### CLI / preset tests

至少覆盖：

- `tests/test_api_cli.py` 中追加 focused preset tests
- listing 包含 `block-read-full`
- `task run --preset ...` 走到 `manager.block_read_full(...)`
- CLI 显式 `--block-code` 覆盖 preset 默认值
- 缺少 `block_code` 的 preset 稳定失败
- unsupported preset command 仍稳定失败

### Non-Goals for Tests

这条线不需要新增：

- provider tests
- replay fixture tests
- catalog tests
- export tests

因为这些已经由 `task block-read-full` 或其他既有功能覆盖。

## Risks / Trade-offs

- [把 preset 接入做成第二套解析系统]
  - 通过复用现有 `_build_task_preset_namespace(...)` 来规避
- [把 `block-read-full` 错误扩展成导出型 preset]
  - 通过把 task-specific options 限定为 `block_code` 来规避
- [为了这一个 task 扩 preset schema]
  - 明确第一版不引入模板变量、路径插值和动态命名
- [把 catalog 过早拉进来]
  - 明确这条线只做 task preset，不做 catalog
- [把 `profile/api_profile` 产品化边界做大]
  - 通过保持这些为现有 schema 的被动兼容字段，而不是本包新增能力来规避
- [preset 配置错误被延后到更深层 dispatch]
  - 通过对缺少 `block_code` 的 `block-read-full` preset 增加显式早失败来规避

## Open Questions

第一版无开放问题。范围固定为：

- 现有 task preset 体系
- 新增 `block-read-full` 作为允许目标命令
- 静态 `block_code` 默认值
