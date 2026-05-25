## Why

E-06 provider replay status already exposes failed probe counts and the failed probe list, but compact consumers still need to inspect the list to identify the first failed target. A single primary failed probe hint keeps the summary useful without exposing full probe payloads or implying recovery behavior.

## What Changes

- Add additive `runtime.probe_summary.primary_failed_probe`.
- Derive the value from the existing ordered `failed` probe list.
- Preserve the field in CLI `provider-replay status --view summary`, which already projects the compact `probe_summary`.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-06 remains `[部分实现]`
- No provider mutation, socket start, probe endpoint, scheduling, restart, or daemon lifecycle management is introduced.
