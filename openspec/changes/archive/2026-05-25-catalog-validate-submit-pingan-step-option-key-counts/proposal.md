## Why

E-11 records fixed task/report bundle entry coverage in `FUNCTION_TREE.md`. Existing catalog validation reports submit-once and PingAn bundle label/source/name/source-name/entry counts, but it does not show whether those subsets carry step option keys. This makes it harder to distinguish structural coverage from executable readiness without reading the full runtime JSON.

## What Changes

- Add additive `submit_once_bundle_step_option_key_counts` to `catalog validate` detailed and summary payloads.
- Add additive `pingan_bundle_step_option_key_counts` to `catalog validate` detailed and summary payloads.
- Keep both fields read-only and derived only from selected resolved bundle definitions.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-11 remains `[部分实现]`
- No catalog entry, task, report, trade, or bundle step execution is introduced.
