# TdxQuant Command Catalog 使用说明

本文记录统一 command catalog 入口，用于把已经稳定的 `report` / `trade` / `task` preset 再收口成一个更短的日常命令目录层，并进一步支持多步骤 bundle 日常编排。

## 1. 定位

catalog 不是新的 manager。

它当前做两件事：

- 统一列出高频日常命令入口
- 把单条 entry 或多步骤 bundle 映射回既有的 `report` / `trade` / `task` preset 执行链
- 提供零副作用的执行计划预览

边界约定：

- catalog 不直接调用 `bridge.py`
- catalog 不新增新的交易或报表业务逻辑
- entry 仍然只是统一索引层
- bundle 只是把多个既有 entry 按固定顺序串起来，底层仍然走原有 preset 分发路径
- `plan` 只做解析，不触发任何真实 workflow

## 2. 配置文件

catalog 使用独立配置文件：

- [runtime/command-catalog.json](/opt/iflow/TdxQuant/runtime/command-catalog.json:1)
- [runtime/command-bundles.json](/opt/iflow/TdxQuant/runtime/command-bundles.json:1)

每个 entry 当前包含：

- `source`
  - `report`
  - `trade`
  - `task`
- `preset`
  - 对应 source 下已经存在的 preset 名称
- `description`
  - 可选说明文字
- `labels`
  - 可选标签数组
  - 用于按用途筛选，例如 `report`、`morning`、`diagnostics`

示例：

```json
{
  "daily-review": {
    "source": "report",
    "preset": "daily-review"
  },
  "turbo-buy": {
    "source": "trade",
    "preset": "turbo-buy"
  },
  "guarded-buy": {
    "source": "task",
    "preset": "guarded-default"
  }
}
```

bundle 示例：

```json
{
  "refresh-review": {
    "description": "先刷新环境，再查看最近台账摘要。",
    "labels": ["morning", "review", "maintenance"],
    "steps": [
      {"name": "refresh", "entry": "refresh-env"},
      {"name": "review", "entry": "recent-ledger", "options": {"limit": 10}}
    ]
  }
}
```

其中：

- `name`
  - 可选稳定 step 名称
  - 用于 `--from-step` / `--to-step` / `--only-step`
  - 如果不写，默认使用 `entry` 名称

## 3. CLI 调用

### 3.1 查看统一入口

```bash
python -m tdxquant.cli catalog list
python -m tdxquant.cli catalog list --entry turbo-buy
python -m tdxquant.cli catalog list --bundle refresh-review
python -m tdxquant.cli catalog list --kind all
python -m tdxquant.cli catalog list --kind all --view summary
python -m tdxquant.cli catalog list --kind bundle --label diagnostics
python -m tdxquant.cli catalog list --kind entry --label report
```

返回中会包含：

- `entries`
  - 单条入口列表
- `bundles`
  - 多步骤 bundle 列表
  - 每个 step 现在会返回 `index`、`name`、`entry`

如果传 `--label`，只会返回带该标签的 entry / bundle。

列表结果现在会稳定排序：

- 先按 `labels` 数量降序
- 再按 `name` 升序

如果你只是想快速扫一眼可用入口，可以显式加：

```bash
python -m tdxquant.cli catalog list --kind all --view summary
```

此时输出会裁剪为更适合发现入口的字段：

- entry
  - `name`
  - `source`
  - `command`
  - `labels`
  - `description`
- bundle
  - `name`
  - `labels`
  - `step_count`
  - `step_names`
  - `description`

### 3.2 执行 report entry

```bash
python -m tdxquant.cli catalog run --entry daily-review
python -m tdxquant.cli catalog run --entry period-review --start-date 2026-04-20 --end-date 2026-04-26
python -m tdxquant.cli catalog run --entry daily-review --view summary
```

这类调用最终仍然走：

- `report run --preset ...`

### 3.3 执行 trade entry

```bash
python -m tdxquant.cli catalog run \
  --entry turbo-buy \
  --code 516820 \
  --price 0.35 \
  --quantity 100

python -m tdxquant.cli catalog run \
  --entry turbo-buy \
  --code 516820 \
  --price 0.35 \
  --quantity 100 \
  --view summary
```

如需临时覆盖 preset 中的固定环境参数，可以继续显式传参：

```bash
python -m tdxquant.cli catalog run \
  --entry turbo-buy \
  --port COM9 \
  --code 516820 \
  --price 0.35 \
  --quantity 100
```

这类调用最终仍然走：

- `trade run --preset ...`

### 3.4 执行 task entry

```bash
python -m tdxquant.cli catalog run \
  --entry guarded-buy \
  --code 516820 \
  --price 0.35 \
  --quantity 100
```

这类调用最终仍然走：

- `task run --preset ...`

### 3.5 执行 bundle

```bash
python -m tdxquant.cli catalog run --bundle refresh-review
python -m tdxquant.cli catalog run \
  --bundle guarded-review-buy \
  --code 516820 \
  --price 0.35 \
  --quantity 100
```

这类调用的执行方式是：

1. 先解析 bundle
2. 顺序解析其中每个 step 引用的 entry
3. 每个 step 继续回落到既有的 `report run --preset ...` / `trade run --preset ...` / `task run --preset ...`
4. 任一步失败就停止后续 step

如果传了顶层 `--output`，写出的是整体 bundle 汇总结果，不会把同一个输出路径透传给每个 step。

### 3.6 局部执行 bundle step

如果你不想每次都从第一步开始，可以按 step 名称或 1-based 序号选择范围：

```bash
python -m tdxquant.cli catalog run --bundle refresh-review --only-step review
python -m tdxquant.cli catalog run --bundle guarded-review-buy --from-step review
python -m tdxquant.cli catalog run --bundle guarded-review-buy --from-step 1 --to-step 1
```

规则：

- `--only-step`
  - 只执行一个 step
- `--from-step` + `--to-step`
  - 执行一个连续区间
- `--from-step` 单独使用
  - 从该 step 一直执行到 bundle 末尾
- `--to-step` 单独使用
  - 从 bundle 起点执行到该 step
- `--only-step` 不能和 `--from-step` / `--to-step` 同时使用
- 如果 step 名称不存在，或起止范围反了，命令会直接报 `invalid_request`

### 3.7 执行前预览计划

如果你想先看最终会跑什么，而不真正执行，可以使用 `catalog plan`：

```bash
python -m tdxquant.cli catalog plan --entry daily-review
python -m tdxquant.cli catalog plan --entry turbo-buy --port COM9 --code 516820 --price 0.35 --quantity 100
python -m tdxquant.cli catalog plan --bundle guarded-review-buy --only-step review
python -m tdxquant.cli catalog plan --bundle guarded-review-buy --only-step review --view summary
```

这个命令会返回：

- entry 或 bundle 的解析结果
- 实际将要分发到哪个 `source` / `preset` / `command`
- 显式 CLI 参数覆盖之后的 `resolved_args`
- bundle 场景下的选中 step 范围与每步解析结果

边界约定：

- `catalog plan` 不会调用 `report` / `trade` / `task` 实际 handler
- 它只验证 catalog、bundle、preset 和参数合并是否符合预期
- 它不保证底层 workflow 一定成功，只保证入口层解析结果清晰可见

### 3.8 摘要视图

如果你只想看更短的终端结果，可以对 `catalog list`、`catalog run` 或 `catalog plan` 显式加：

```bash
--view summary
```

这个视图会保留高信号字段，例如：

- entry / bundle 名称
- 成功失败状态
- 分发到的 `source` / `preset` / `command`
- bundle 选中 step 范围和每步状态
- 关键参数，如 `code`、`price`、`quantity`、`date`
- 可解析时的 `contract_no`

边界约定：

- 默认仍是 `--view detailed`
- `summary` 只影响最终打印/写出的 JSON 视图
- 实际执行逻辑、退出码、合同号日志、内部 `Result` 判定都不变

## 4. 默认套路建议

当前默认 registry 已经补了几条更贴近日常使用的 bundle：

- `morning-review`
  - 开盘前刷新环境并查看当日交易日报
- `failure-review`
  - 排障时先看最近失败台账，再回看当日交易日报
- `audit-rejection-diagnostics`
  - 排障时先看最近失败台账，再回看当日拒单 trade_audit 诊断
- `audit-confirmed-review`
  - 查看当日成功成交日报并回看当日已确认 trade_audit 复盘
- `audit-replay-review`
  - 查看最近台账摘要并回看当日 replayed trade_audit 复盘
- `audit-failure-diagnostics`
  - 先看最近失败台账，再回看当日 failed trade_audit 诊断复盘
- `audit-exception-diagnostics`
  - 先看最近失败台账，再回看当日 rejected + failed trade_audit 异常复盘
- `audit-confirm-exception-diagnostics`
  - 先看最近失败台账，再回看当日 confirm_current rejected + failed trade_audit 异常复盘
- `audit-pingan-confirm-exception-diagnostics`
  - 先看最近失败台账，再回看当日平安券商 confirm_current rejected + failed trade_audit 异常复盘
- `audit-submit-once-exception-diagnostics`
  - 先看最近失败台账，再回看当日 buy_submit_once rejected + failed trade_audit 异常复盘
- `audit-pingan-submit-once-exception-diagnostics`
  - 先看最近失败台账，再回看当日平安券商 buy_submit_once rejected + failed trade_audit 异常复盘
- `audit-buy-exception-diagnostics`
  - 先看最近失败台账，再回看当日 buy rejected + failed trade_audit 异常复盘
- `audit-sell-exception-diagnostics`
  - 先看最近失败台账，再回看当日 sell rejected + failed trade_audit 异常复盘
- `audit-submit-path-exception-diagnostics`
  - 先看最近失败台账，再回看当日 submit path rejected + failed trade_audit 异常复盘
- `audit-pingan-submit-path-exception-diagnostics`
  - 先看最近失败台账，再回看当日平安券商 submit path rejected + failed trade_audit 异常复盘
- `audit-pingan-order-exception-diagnostics`
  - 先看最近失败台账，再回看当日平安券商 buy + sell rejected + failed trade_audit 异常复盘
- `guarded-trade-followup`
  - 受保护买入后继续看最近台账与当日成功成交
- `submit-once-followup`
  - 完整提交后继续看最近台账与当日成功成交
- `submit-ready-audit-review`
  - 推进到提交确认前边界后继续回看当日 trade_audit 复盘
- `submit-ready-exception-review`
  - 推进到提交确认前边界后继续回看当日 rejected + failed trade_audit 异常复盘
- `confirm-audit-review`
  - 推进当前确认框后继续回看当日 trade_audit 复盘
- `confirm-complete-review`
  - 推进当前确认框后继续查看当日成功成交日报和已确认 trade_audit 复盘
- `confirm-exception-review`
  - 推进当前确认框后继续回看当日 confirm_current rejected + failed trade_audit 异常复盘
- `confirm-pingan-exception-review`
  - 推进当前确认框后继续回看当日平安券商 confirm_current rejected + failed trade_audit 异常复盘
- `submit-once-exception-review`
  - 完整提交流程后继续回看当日 buy_submit_once rejected + failed trade_audit 异常复盘
- `submit-once-pingan-exception-review`
  - 完整提交流程后继续回看当日平安券商 buy_submit_once rejected + failed trade_audit 异常复盘
- `guarded-buy-exception-review`
  - 受保护买入后继续回看当日 buy rejected + failed trade_audit 异常复盘
- `confirm-submit-path-exception-review`
  - 推进当前确认框后继续回看当日 submit path rejected + failed trade_audit 异常复盘
- `confirm-pingan-submit-path-exception-review`
  - 推进当前确认框后继续回看当日平安券商 submit path rejected + failed trade_audit 异常复盘

推荐用法：

- 早盘检查：
  - `python -m tdxquant.cli catalog list --kind bundle --label morning`
- 排障：
  - `python -m tdxquant.cli catalog list --kind bundle --label diagnostics`
- 交易后跟踪：
  - `python -m tdxquant.cli catalog list --kind bundle --label followup`

## 5. 参数覆盖规则

catalog 本身不解释业务参数，只做透传或补默认值。

entry 执行顺序仍然是：

1. catalog entry 解析为下游 source + preset
2. 下游 preset 提供默认值
3. 当前命令显式 CLI 参数覆盖 preset 默认值
4. 下游命令组再补最终兜底默认值

这意味着：

- 你可以继续用 catalog 固定大部分环境参数
- 真正动态的值仍然只在执行时传入

bundle 下再多一层：

1. bundle step `options` 先补空值
2. 当前命令显式 CLI 参数继续覆盖这些 step 默认值
3. step 对应的下游 preset 再补自身默认值

所以 bundle 里的 `options` 仍然只是默认模板，不会压过你命令行里显式传入的值。

局部执行时也是同一套规则，只是只对选中的 step 生效。

`catalog plan` 看到的也是这同一套合并结果，因此可以用它来确认实际执行前的最终参数状态。

`--view summary` 只是把这份结果再裁成更适合终端快速查看的形状。

## 6. 与其他层的关系

- `trade/report/task preset`
  - 命令组内部模板
- `catalog`
  - 跨命令组统一目录与 bundle 编排层
- `profile`
  - workflow 内部默认行为

推荐理解方式：

- 要定义某个命令组自己的模板，用 preset
- 要给日常使用一个统一短入口，再把 preset 收口到 catalog entry
- 要把 2-3 条固定日常命令进一步串起来，用 catalog bundle
