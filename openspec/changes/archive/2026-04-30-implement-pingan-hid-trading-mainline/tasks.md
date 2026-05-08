## 1. PingAn HID mainline core

- [x] 1.1 Implement `PingAn` sell submit-once execution in `desktop/uia.py`, `trade/manager.py`, and `PingAnDesktopTraderGateway`.
- [x] 1.2 Ensure fast-path and submit-once `buy/sell` flows share the existing finalized artifact, audit, and canonical trader store integration.
- [x] 1.3 Add or extend manager/gateway tests for sell submit-once, method naming, and artifact propagation.

## 2. Trade CLI and presets

- [x] 2.1 Add stable `trade sell` and `trade sell-submit-once` commands that route through the current PingAn live-trading mainline.
- [x] 2.2 Extend `runtime/trade-presets.json` and related CLI preset resolution to support sell and sell-submit-once defaults.
- [x] 2.3 Add CLI tests covering the new sell command surfaces and preset execution paths.

## 3. Task workflows and presets

- [x] 3.1 Add stable `trade_sell` and `trade_sell_submit_once` task workflows plus matching `task trade-sell` and `task trade-sell-submit-once` CLI entrypoints.
- [x] 3.2 Extend task preset mapping and `runtime/task-presets.json` to support the new sell-oriented workflows.
- [x] 3.3 Add task-layer tests covering sell workflow dispatch, refresh orchestration, and safety-control passthrough.

## 4. Documentation and verification

- [x] 4.1 Update function map, usage docs, and any relevant runtime command references to state that live trading now centers on `PingAN + HID`.
- [x] 4.2 Run targeted pytest coverage for manager/gateway/CLI/task changes and validate the OpenSpec change strictly.
