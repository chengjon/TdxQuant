# Review: Task Block Read Watchlist Export Preset Design

审阅日期: 2026-05-05
审阅对象: `docs/superpowers/specs/2026-05-05-task-block-read-watchlist-export-preset-design.md`

---

## 总评

这份 spec 目标清晰、边界克制、工程风险低。核心思路（只把 `block-read-watchlist-export` 加入现有 task preset allowlist）完全正确。以下分三个维度展开：设计合理性、实现表面完整性、建议补充项。

---

## 1. 设计合理性 — 通过

### 做对了的事

- **最小接入策略正确。** 当前 `TASK_COMMAND_DEFAULT_PROFILES` 只有 8 个条目，`_build_task_preset_namespace` 的 allowlist 检查（`cli.py:3555`）是唯一的前门。spec 准确识别了这个入口，没有提议另开分支。
- **不修改 preset schema 的决定合理。** 现有 `_normalize_task_preset` 已经能处理 `block_code`、`output`（通过 `options` dict）、`overwrite`（布尔值）这些静态字段，不需要任何 schema 扩展。
- **CLI 显式参数覆盖 preset 默认值的语义已落地。** `_build_task_preset_namespace` 在 `cli.py:3558-3561` 已经实现了 "preset 填缺省值，CLI 覆盖非 None 值" 的合并逻辑，spec 描述的覆盖行为与代码实际一致。
- **Non-Goals 列表干净。** 不引入模板变量、不新增 catalog、不动 provider — 每一条都在降低范围蔓延风险。

### 一个轻微的语义不一致

spec 的 Preset Contract 示例中使用了 `"overwrite": false`（布尔值），但 CLI parser 定义（`cli.py:999`）使用的是 `action="store_true", default=False`。这意味着 `overwrite` 的 argparse 存储值为 `True` 或 `False`。

preset 合并逻辑在 `cli.py:3559-3561`：

```python
for key, value in resolved_preset.get("options", {}).items():
    if key not in merged or merged.get(key) is None:
        merged[key] = value
```

由于 argparse 对 `--overwrite` 不传时默认值为 `False`（不是 `None`），preset 中的 `"overwrite": true` **永远不会生效** — CLI 的 `False` 会挡住 preset 的 `True`。

这不是 spec 的设计错误，而是 spec 没有显式标注这个现有行为。建议在 spec 中补充一条说明，明确 `overwrite` 字段的覆盖语义受 argparse `default=False` 影响，并建议将 argparse default 改为 `None` 以让 preset 值有机会填入。

---

## 2. 实现表面完整性 — 需要补充

spec 列出了 4 个实现面。逐项核对：

### 2.1 `tdxquant/tasking.py` — 正确

在 `TASK_COMMAND_DEFAULT_PROFILES` 中加入 `"block-read-watchlist-export": "default"` 即可。这是唯一必需的 allowlist 改动。

**建议补充**：spec 应明确写入默认 profile 值。参考现有条目的模式，`"default"` 是合理选择，但 spec 里没有写死。

### 2.2 `tdxquant/cli.py` — 不完整

spec 说"复用现有 `_build_task_preset_namespace` 和 `_handle_task_subcommand`"，但没有提到一个关键细节：

`_build_task_preset_namespace` 中 `cli.py:3558-3561` 的合并逻辑使用的是 preset `options` 的 key 名直接映射到 argparse namespace 属性名。但 `block-read-watchlist-export` 的 CLI 参数有 `dest="export_output"` 的重命名（`cli.py:998`）：

```python
task_block_read_watchlist_export_parser.add_argument("--output", dest="export_output", required=True)
```

这意味着 preset `options` 中如果写 `"output": "runtime/exports/zxg.json"`，合并后写入的是 `merged["output"]`，而 dispatch 读取的是 `args.export_output`。**preset 值无法到达 dispatch 调用点。**

spec 需要补充以下两种方案之一：

- **方案 A**：preset `options` 中使用 `"export_output"` 而不是 `"output"`，匹配 argparse `dest` 名。
- **方案 B**：在 `_build_task_preset_namespace` 中为 `block-read-watchlist-export` 增加一个字段映射步骤 `output → export_output`。

推荐方案 A，因为它不需要修改 `cli.py` 的合并逻辑，只需在 preset JSON 和 spec 示例中使用正确的 key 名。

### 2.3 `runtime/task-presets.json` — 正确但示例需调整

如果采用方案 A，示例应改为：

```json
{
  "export-zxg-watchlist": {
    "command": "block-read-watchlist-export",
    "description": "Export ZXG watchlist snapshot to a fixed JSON path",
    "profile": "default",
    "api_profile": "safe_read",
    "options": {
      "block_code": "ZXG",
      "export_output": "runtime/exports/zxg.json",
      "overwrite": false
    }
  }
}
```

### 2.4 Tests — 正确但可更精确

spec 列出的 4 条测试覆盖是合理的。建议补充第 5 条：

- **preset `options` 中的 `export_output` 正确传递到 `manager.block_read_watchlist_export(output=...)`**

这条验证的是 2.2 中提到的 key 名映射问题，是最容易出错的地方。

---

## 3. 建议补充项

### 3.1 `_build_task_preset_namespace` 中 `block-read-watchlist-export` 的必需参数验证

现有代码对 `trade-buy` 等命令在 `cli.py:3598-3601` 做了必需参数检查：

```python
if command_name in {"trade-buy", "trade-submit-once", ...}:
    missing_required = [name for name in ("port", "code", "price", "quantity") if merged.get(name) is None]
    if missing_required:
        raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")
```

spec 没有提到 `block-read-watchlist-export` 是否需要类似的必需参数验证。当前 argparse 已经把 `--block-code` 和 `--output`（`dest="export_output"`）设为 `required=True`，所以当通过 preset 执行时，如果 preset 中没有提供这些字段，会走到 dispatch 时才发现缺失。

建议：spec 明确是否需要在 `_build_task_preset_namespace` 中加入 `block_code` + `export_output` 的缺失检查。两种选择都可行，但应该在 spec 里说清楚。

### 3.2 profile 字段的默认值

`_normalize_task_preset` 在 `tasking.py:106` 中用 `TASK_COMMAND_DEFAULT_PROFILES.get(command)` 作为 profile fallback。如果 `block-read-watchlist-export` 加入 registry 时 profile 设为 `"default"`，而 preset 中也写了 `"profile": "default"`，最终行为一致。但如果用户 preset 省略 `profile`，会从 registry 取。

spec 的 Preset Contract 示例写了 `"profile": "default"`，但没有解释为什么选 `"default"` 而不是省略让 registry 决定。建议加一句说明，或直接让示例省略 `profile` 字段以展示 registry fallback 行为。

### 3.3 `_handle_task_subcommand` dispatch 分支

spec 说"最终复用现有 dispatch: `manager.block_read_watchlist_export(...)`"，这是正确的 — `cli.py:3694-3699` 已经有这个分支。但 spec 没有显式标注"这里不需要改动"。建议在 Implementation Surface 中加一行"无需改动"的确认，让实现者知道这个分支已经就位。

---

## 总结

| 维度 | 评定 | 说明 |
|------|------|------|
| 设计方向 | ✅ 通过 | 最小接入策略完全正确 |
| 实现表面覆盖 | ⚠️ 需补充 | `output` → `export_output` key 名映射问题未覆盖 |
| 风险控制 | ✅ 通过 | Non-Goals 清晰，scope 收敛 |
| 测试覆盖 | ⚠️ 建议补充 | 缺 preset key 名传递验证 |
| 文档精度 | ⚠️ 建议调整 | `overwrite` 覆盖语义、`profile` 默认值说明需补充 |

**结论**：spec 可以进入实现，但建议先补充 `export_output` key 名映射的处理方案和 `overwrite` 覆盖语义说明后再动手。
