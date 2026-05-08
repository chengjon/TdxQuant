# Task Block Read Watchlist Export Preset Design

Date: 2026-05-05

## Context

`task block-read-watchlist-export` 已经落地为稳定的导出型 task 入口，解决了：

- provider-level `block.read_watchlist_snapshot(...)`
- 单文件 JSON 导出
- 默认拒绝覆盖
- 薄 `data.export` 元数据

当前还缺一层“日常复用”的入口：把固定 `block_code + export_output + overwrite` 这类重复参数配置接进现有 task preset 体系，避免用户每次手工重复输入完整命令。

这条线不应反向改动 task preset 基础模型，也不应提前把 catalog / 模板变量 / 路径插值混进来。第一版只解决一件事：

- 让 `block-read-watchlist-export` 成为现有 `task run --preset ...` 的合法目标命令

## Goals

- 把 `block-read-watchlist-export` 接入现有 task preset 体系
- 继续复用：
  - `runtime/task-presets.json`
  - `resolve_task_preset(...)`
  - `task run --preset ...`
- 第一版 preset 只支持静态默认值：
  - `block_code`
  - `export_output`
  - `overwrite`
- 显式 CLI 参数继续覆盖 preset 默认值

## Non-Goals

- 不修改 task preset schema
- 不支持模板变量或路径占位符
- 不支持运行时插值
- 不新增 catalog entry
- 不新增 provider capability
- 不新增新的导出格式

## Recommended Approach

采用最小接入方案：

- 只把 `block-read-watchlist-export` 加入 task preset allowlist
- 继续复用现有 task preset 合并与 dispatch 逻辑
- 不为它单独发明第二套 preset 解析路径

原因：

- 当前缺口不是“preset 系统不够强”，而是“新 task 尚未成为 preset 合法目标”
- 这样最稳，也最符合现有 task preset 的职责

## Preset Contract

第一版 preset 条目继续沿用当前 task preset 结构，例如：

```json
{
  "export-zxg-watchlist": {
    "command": "block-read-watchlist-export",
    "description": "Export ZXG watchlist snapshot to a fixed JSON path",
    "api_profile": "safe_read",
    "options": {
      "block_code": "ZXG",
      "export_output": "runtime/exports/zxg.json",
      "overwrite": false
    }
  }
}
```

关键约束：

- `command` 必须是：
  - `block-read-watchlist-export`
- `options` 第一版只允许静态默认值
- 第一版预期字段为：
  - `block_code`
  - `export_output`
  - `overwrite`

不支持：

- `{{date}}`
- `${ENV_VAR}`
- 自动生成文件名
- 多 block 批量导出

## CLI Semantics

### Listing

`task presets` 应能够列出指向 `block-read-watchlist-export` 的 preset。

### Execution

`task run --preset export-zxg-watchlist` 最终仍然应 dispatch 到：

- `TdxTaskManager.block_read_watchlist_export(...)`

而不是新增一条 preset 专用执行路径。

### Override Rules

显式 CLI 参数必须继续覆盖 preset 默认值。

这里需要明确区分两层 `output` 语义：

- `task block-read-watchlist-export` 直跑命令使用 `--output`
- `task run` 已经把 `--output` 用作“整条命令 JSON 结果写盘路径”

因此，这条 preset 线不应让 `task run` 继续复用同名 `--output` 来承载导出目标文件。推荐做法是：

- preset `options` 使用内部字段名 `export_output`
- `task run` 如需显式覆盖导出目标，新增专用参数：
  - `--export-output`

例如：

```bash
python -m tdxquant.cli task run \
  --preset export-zxg-watchlist \
  --export-output runtime/exports/zxg-override.json \
  --overwrite
```

则最终调用应以 CLI 显式参数为准：

- `output=runtime/exports/zxg-override.json`
- `overwrite=True`

而不是使用 preset 中的默认 `export_output` / `overwrite`

## Implementation Surface

这条线我建议只动 4 个面。

### 1. `tdxquant/tasking.py`

更新 `TASK_COMMAND_DEFAULT_PROFILES`，把：

- `block-read-watchlist-export`

加入现有 task preset 支持命令集合。

这一点很关键，因为当前 `task run --preset ...` 的 allowlist 判断依赖这个 registry。

默认 profile 建议固定为：

- `"default"`

### 2. `tdxquant/cli.py`

复用现有 `_build_task_preset_namespace(...)` 和 `_handle_task_subcommand(...)` 逻辑，不新开分支模型。

需要确保：

- preset 解析后能把 `task_command` 设置为 `block-read-watchlist-export`
- preset `options.export_output` 能正确映射到 dispatch 读取的 `args.export_output`
- `task run` 的显式 `--export-output` 能覆盖 preset 默认值
- `task run` 的 `--overwrite` 应采用可区分“未显式提供”的语义
  - 推荐 `argparse.BooleanOptionalAction`
  - 默认值设为 `None`
- 最终复用现有 dispatch：
  - `manager.block_read_watchlist_export(...)`

这里还要明确一点：

- 现有 `_handle_task_subcommand(...)` 中
  - `task block-read-watchlist-export -> manager.block_read_watchlist_export(...)`
  的 dispatch 分支已经存在
- 因此本包的 CLI 重点不是新增 dispatch 分支，而是让 preset 合并后的 namespace 正确到达这个已有分支

### 3. `runtime/task-presets.json`

新增至少一个 representative preset 示例，固定：

- `block_code`
- `export_output`
- `overwrite`

目的不是提供最终业务模板集合，而是确保：

- 这条命令能真实进入 task preset 体系
- 列表和运行路径都有真实样例

### 4. Tests

focused tests 只补 preset 这条链：

- `task presets` 列表中能出现该命令
- `task run --preset ...` 能正确 dispatch 到 `manager.block_read_watchlist_export(...)`
- preset `options.export_output` 能正确传到 `manager.block_read_watchlist_export(output=...)`
- CLI 显式 `--export-output` / `--overwrite` 能覆盖 preset 默认值
- preset target 若不在 allowlist 中，继续按当前 invalid-request 语义失败
- 如果 preset 缺少 `block_code` 或 `export_output`，应在 preset execution 阶段稳定失败，而不是等到更深层 dispatch 再报不明确错误

## Testing

### CLI / preset tests

至少覆盖：

- listing 包含 `block-read-watchlist-export`
- `task run --preset ...` 走到 `manager.block_read_watchlist_export(...)`
- CLI 显式参数覆盖 preset 默认值
- 缺少 `block_code` / `export_output` 的 preset 稳定失败
- unsupported preset command 仍稳定失败

### Non-Goals for Tests

这条线不需要新增：

- provider tests
- replay fixture tests
- catalog tests
- 文件导出内容测试

因为这些已经由 `task block-read-watchlist-export` 本身覆盖。

## Risks / Trade-offs

- [把 preset 接入做成第二套解析系统]
  - 通过复用现有 `_build_task_preset_namespace(...)` 来规避
- [把 preset 的导出路径错误写进通用 JSON result `--output`]
  - 通过固定使用 `export_output` 内部字段和专用 `--export-output` 覆盖参数来规避
- [布尔 `overwrite` 无法从 preset 生效]
  - 通过要求 `task run` 使用 `BooleanOptionalAction + default=None` 的覆盖语义来规避
- [为了这一个 task 扩 preset schema]
  - 明确第一版不引入模板变量、路径插值和动态命名
- [把 catalog 过早拉进来]
  - 明确这条线只做 task preset，不做 catalog

## Open Questions

第一版无开放问题。范围固定为：

- 现有 task preset 体系
- 新增 `block-read-watchlist-export` 作为允许目标命令
- 静态默认值
