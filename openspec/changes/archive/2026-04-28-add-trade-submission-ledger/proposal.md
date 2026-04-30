## Why

当前 `submission_key` 只是关联字段，还不能真正阻止同一笔桌面交易被重复提交。既然交易线已经有稳定安全摘要和持久化状态，下一步就应该把 `submission_key` 升级成真正可落地的幂等账本。

## What Changes

- Add a durable desktop-trade submission ledger for stable Ping An buy workflows.
- Make `submission_key` idempotent for stable desktop trade workflows:
  - same key + same trade request + previous side-effecting attempt => short-circuit without re-clicking the desktop
  - same key + different trade request after a side-effecting attempt => reject as a conflict
- Persist submission-ledger rows as a durable local artifact and surface the ledger path in trade results.
- Extend `trade_safety` to include a normalized idempotency summary for executed, skipped, and conflict-rejected keyed requests.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-idempotency`: Defines durable submission-ledger behavior for stable desktop trading, including duplicate short-circuit and conflicting-key rejection.

### Modified Capabilities
- `tdx-desktop-trading-safety`: Extends the stable trade safety contract to include normalized idempotency summary metadata.
- `tdx-desktop-trading-management`: Extends stable trade manager workflows to consult and persist the submission ledger.

## Impact

- Affected code:
  - `tdxquant/trade/context.py`
  - `tdxquant/trade/manager.py`
  - `tdxquant/trade/__init__.py`
  - `tdxquant/cli.py`
  - `tests/test_trade_manager.py`
  - `tests/test_api_cli.py`
- New runtime artifact:
  - `runtime/pingan-submission-ledger.jsonl`
- Affected docs:
  - trade function map
  - next-steps documentation
