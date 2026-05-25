## Why

E-06 provider replay status exposes detailed probe counts and lists, but callers still need to compare `requested_count` with `total_count` to understand whether probe coverage is absent, partial, or complete. A compact request coverage status improves operator readability without adding new probes or daemon lifecycle behavior.

## What Changes

- Add additive `probe_summary.request_coverage_status`.
- Derive the value from existing probe counts: `none`, `partial`, or `complete`.
- Preserve the field in CLI `provider-replay status --view summary`, which already projects the compact `probe_summary`.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-06 remains `[部分实现]`
- No provider mutation, socket start, probe endpoint, scheduling, restart, or daemon lifecycle management is introduced.
