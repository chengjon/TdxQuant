## Why

`FUNCTION_TREE.md` E-01 still marks subscription query-style one-shot CLI as partial because replay mode rejects `api subscription-subscribe`, `api subscription-unsubscribe`, and `api subscription-list`. The CLI also needs a real manager-level one-shot path, not only mocked dispatch tests.

## What Changes

- Add built-in replay fixtures for `subscription.subscribe_hq`, `subscription.unsubscribe_hq`, and `subscription.get_subscribe_hq_stock_list`.
- Register those fixtures in the provider replay catalog and default sync replay fixture map.
- Add manager-level `RuntimeManager` one-shot methods that preserve live one-shot session behavior and use replay dispatch in replay mode.
- Allow nested `api subscription-subscribe/unsubscribe/list --provider-mode replay` to use fixture-backed manager replay.
- Update `FUNCTION_TREE.md` E-01 evidence and boundary without implying foreground watch, background worker, SSE, or reconnect/backoff governance is included.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-replay-fixtures`: add representative one-shot subscription replay fixtures.
- `tdx-provider-replay-mode`: add default fixture-backed replay execution for one-shot subscription capabilities.
- `tdx-api-management`: expose manager-level one-shot subscription methods in live and replay modes.
- `tdx-api-cli-entry`: allow explicit replay mode for one-shot subscription API commands.
- `tdx-subscription-query-one-shot-cli`: clarify that one-shot commands may be exercised through replay fixtures without becoming long-running watch governance.

## Impact

- Affected code: `tdxquant/replay_fixtures.py`, `tdxquant/replay_provider.py`, `tdxquant/api/manager.py`, `tdxquant/cli.py`.
- Affected fixtures: `tdxquant/fixtures/provider/`.
- Affected tests: replay fixture, replay provider, API manager/CLI tests.
- Affected documentation/register: `FUNCTION_TREE.md` remains the single feature registry.
