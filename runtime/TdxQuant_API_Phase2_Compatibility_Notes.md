# TdxQuant API 第二阶段兼容性与范围说明

## 本次新增纳入新体系的能力

本次在第一阶段 `market/meta` 的基础上，继续纳入了以下能力：

- `formula` 域
  - `formula-format-data`
  - `formula-set-data`
  - `formula-set-data-info`
  - `formula-get-data`
  - `formula-zb`
  - `formula-xg`
  - `formula-exp`
  - `formula-mul-xg`
  - `formula-mul-zb`
- `block` 域
  - `send-user-block`
- `task` 层
  - `sector-research`
  - `formula-scan`
  - `refresh-environment`

对应代码入口：

- `tdxquant/api/formula.py`
- `tdxquant/api/block.py`
- `tdxquant/api/task.py`
- `tdxquant/api/manager.py`

对应顶层 Python 入口：

- `from tdxquant.api import TdxApiManager`
- `from tdxquant.api import TdxTaskManager`

## 新 CLI 入口

本次新增和扩展的嵌套 CLI 入口：

- `python -m tdxquant.cli api ...`
  - 现在除了 `market/meta` 读接口，也支持 `formula` 和 `block`
- `python -m tdxquant.cli task ...`
  - 提供稳定场景任务入口

示例：

```bash
python -m tdxquant.cli api formula-xg --formula-name MY_FORMULA
python -m tdxquant.cli api send-user-block --block-code ZXG --stock 000001
python -m tdxquant.cli task sector-research --sector 钛金属 --profile sector_research
python -m tdxquant.cli task formula-scan --formula-name MY_FORMULA --code 000001 --code 000002
```

## 保持不变的兼容性结论

- 现有扁平 CLI 命令继续可用
- 旧公式命令继续可用
- 旧 `tdx-send-user-block` 继续可用
- 桌面自动化交易链不受本次改动影响
- `bridge.py` 仍保留为底层透传层
- `_run_tq_call` 仍维持“初始化 -> 执行 -> 关闭”的短连接模式

## 第二阶段边界

本次解决：

- `TdxApiManager` 扩展到四域：`market/meta/formula/block`
- `api` 二级命令承接 `formula/block`
- `task` 层骨架和首批稳定场景
- `task-profiles.json` 独立配置

本次不解决：

- 桌面自动化交易 capability 的统一调度
- `TradeManager`
- `task` 层与桌面交易的混合编排
- 长连接复用
- 全量 CSV 导出体系
- 旧扁平命令废弃或删除
