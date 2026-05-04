# Block Read Watchlist Export Design

Date: 2026-05-04

## Context

provider-level `block.read_watchlist_snapshot(...)` 已经稳定，且 `task block-read-watchlist` 也已落地为薄包装日常入口。当前还缺一层明确的“导出”能力：把标准化 watchlist snapshot 安全写到本地文件，供上层系统或人工流程消费。

这条线不应反向定义 provider contract，也不应在第一版里扩成通用导出框架。第一版只解决一件事：

- 从 TongDaXin 自选板块读取标准化 snapshot
- 以单文件 JSON 的形式安全落盘

## Goals

- 新增独立 task：`task block-read-watchlist-export`
- 输入显式要求：
  - `--block-code`
  - `--output`
  - 可选 `--overwrite`
- 导出内容直接写 provider-level `data.snapshot`
- task 返回保留 `data.snapshot`，并追加薄的 `data.export`
- 默认拒绝覆盖已有文件
- 使用原子写入，失败时不留下半成品文件

## Non-Goals

- 不新增 provider capability
- 不新增 CSV / JSONL / Excel 导出
- 不新增 catalog / preset / bundle
- 不直接写回上层系统
- 不新增 task-only report schema
- 不新增 flat CLI 导出入口

## Recommended Approach

采用独立导出型 task，而不是给 `task block-read-watchlist` 继续叠 `--output`。

原因：

- “纯读 snapshot” 与 “读后写文件” 是两种不同副作用语义
- 独立 task 更容易保持错误 contract 清晰
- 后续若扩 CSV 或批量导出，也有自然演进空间

## CLI / Task Shape

### CLI

```bash
python -m tdxquant.cli task block-read-watchlist-export \
  --block-code ZXG \
  --output runtime/exports/zxg.json
```

支持参数：

- `--block-code` 必填
- `--output` 必填
- `--overwrite` 可选
- 继续复用通用 task 参数，例如 `--profile`、`--api-profile`、`--strategy-path`

### Task manager

新增：

- `TdxTaskManager.block_read_watchlist_export(...)`

推荐签名：

```python
def block_read_watchlist_export(
    self,
    *,
    block_code: str,
    output: str,
    overwrite: bool = False,
) -> Result:
```

内部流程：

1. 调 `manager.block.read_watchlist_snapshot(block_code=...)`
2. 校验目标输出路径
3. 若目标文件存在且未显式 `--overwrite`，稳定失败
4. 将 `data.snapshot` 以 JSON 原子写入 `--output`
5. 返回底层 snapshot contract + `data.export` + 标准 task metadata

第一版不新增 flat CLI，例如：

- `tdx-task-block-read-watchlist-export`

这条线只在 `task` 命名空间暴露。

## Result Contract

### Success

成功时返回：

- 保留底层：
  - `success`
  - `code`
  - `message`
  - `data.snapshot`
  - `warnings`
  - `artifacts`
- task 层继续附加：
  - `data.task`
  - `data.task_profile`
  - `data.timing`
- 导出层新增：
  - `data.export.output_path`
  - `data.export.overwritten`
  - `data.export.file_size`

`data.export.overwritten` 在成功场景下始终存在，取值规则固定为：

- 新建文件：`false`
- 覆盖已有文件（仅在显式 `--overwrite` 时允许）：`true`

### Failure

失败分三类：

1. snapshot 读取失败  
   直接返回底层 provider failure，不尝试写文件。
   推荐 `code`：透传底层 provider failure code。

2. 输出路径冲突或无效  
   例如文件已存在但没给 `--overwrite`、父目录不存在、输出路径是目录、不可写。  
   返回稳定失败，并保留已读取成功的 `data.snapshot`。
   推荐 `code`：`invalid_request`。

3. 写入过程失败  
   例如临时文件写失败、rename 失败。  
   返回稳定失败，并保留已读取成功的 `data.snapshot`。
   推荐 `code`：`execution_failed`。

失败时：

- `data.snapshot` 的存在仅表示 snapshot 读取成功，不表示导出成功
- 调用方必须始终以顶层 `success` 判断导出是否完成
- 不写成功态 `data.export.overwritten`
- 不写成功态 `data.export.file_size`
- 可在 `data.export` 中仅保留：
  - `output_path`
  - `error`

其中 `data.export.error` 在 V1 采用简单字符串，用来承载人类可读的文件侧失败原因；V1 不再额外引入结构化子错误对象。

## File Semantics

### Export content

写入内容仅为：

- provider-level `data.snapshot`

第一版不把整个 envelope 落盘，不混 task metadata，不写 report wrapper。

### JSON serialization

V1 JSON 写盘规则固定为：

- UTF-8
- no BOM
- `ensure_ascii=False`
- `indent=2`
- key 顺序保持 Python dict 插入顺序

这样可以保证：

- `sector_name` 等中文字段保持可读
- `file_size` 有稳定、可解释的物理文件语义
- 人工检查导出文件时不需要再做二次格式化

### Overwrite

- 默认拒绝覆盖
- 只有显式 `--overwrite` 才允许替换已有目标文件

### Directory behavior

- `--output` 必须显式给出
- `--output` 必须指向文件路径，不能是目录
- 父目录必须已存在
- 父目录必须可写
- 实现应对 `--output` 做规范化解析，例如 `realpath`
- 符号链接按标准文件系统解析结果处理
- 第一版不隐式 `mkdir -p`

## Atomic Write Strategy

采用同目录原子写入：

1. 在目标文件同目录创建临时文件
2. 写完整 JSON
3. flush + close
4. 原子发布到最终 `--output`
5. 失败时删除临时文件

临时文件命名应包含随机后缀，例如通过 `NamedTemporaryFile(..., delete=False)` 或等价机制生成，避免并发冲突。

V1 不实现“启动时清理历史残留临时文件”。

这样可以保证：

- 不留下半截 JSON
- 不把失败写入伪装成成功导出

实现语义进一步固定为：

- `overwrite=true`
  - 允许用原子 replace 发布到最终路径
- `overwrite=false`
  - 必须使用等价的 no-clobber 原子发布语义
  - 如果目标文件在 publish 之前或 publish 过程中出现，必须稳定失败为“output already exists”

这意味着 V1 不只是“先检查、再覆盖”，而是要把“拒绝覆盖”落实到最终发布步骤，避免把竞态下新出现的目标文件静默覆盖掉。

## Capability / Replay Boundaries

- 这是 task-layer 场景入口，不注册为新的 provider capability
- 它不会出现在 `runtime.capabilities`
- replay 行为完全依赖底层 `block.read_watchlist_snapshot` 的 replay 模式
- task 层自身不新增独立 replay fixture

## Testing

focused tests 只覆盖这条 task：

### Manager / task

- 成功写 JSON
- snapshot 读取失败时不写文件
- 文件已存在且无 `--overwrite` 时稳定失败
- `--overwrite` 时成功覆盖
- 写入失败时返回失败，但保留 `data.snapshot`
- 写入失败时不留下半成品临时文件
- 成功场景下 `data.export.overwritten` / `data.export.file_size` 语义固定
- `--output` 指向目录或不可写路径时稳定失败
- `overwrite=false` 时，如果目标文件在最终发布前被并发创建，必须稳定失败为 existing-file conflict

### CLI

- `task block-read-watchlist-export --block-code ... --output ...` 解析正确
- dispatch 正确调用 `manager.block_read_watchlist_export(...)`
- JSON 输出保留 `data.snapshot` + `data.export`

### Docs

- task layer usage
- function map / next steps

## Open Questions

第一版无开放问题，范围已经固定为：

- 独立 task
- 单文件 JSON
- 显式输出路径
- 默认拒绝覆盖
