## Why

`trade-submit-ready` 和 `trade-confirm-current` 已经作为稳定 `task` workflow 存在，但它们还没有进入统一的日常入口层。

当前调用方仍然需要显式记住：

- `task trade-submit-ready`
- `task trade-confirm-current`
- 对应的常用默认环境参数

这与现有：

- `guarded-default`
- `task-buy-default`
- `submit-once-default`
- `task-buy`
- `task-submit-once`

的日常使用体验不一致，也让 `catalog` 不能把 split-step 交易 workflow 作为正式的稳定入口暴露出来。

## What Changes

- 为 split-step 交易 workflow 新增稳定 task presets：
  - `submit-ready-default`
  - `confirm-current-default`
- 为 split-step 交易 workflow 新增稳定 command catalog entries：
  - `task-submit-ready`
  - `task-confirm-current`
- 新增一个最小 follow-up bundle，把确认动作和当日 audit review 串成固定入口

## Impact

- 更新 specs：
  - `tdx-task-management`
  - `tdx-command-catalog`
- 影响集中在 runtime 配置与文档：
  - `runtime/task-presets.json`
  - `runtime/command-catalog.json`
  - `runtime/command-bundles.json`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
