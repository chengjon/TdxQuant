## Why

E-11 catalog validation now reports submit-once and PingAn option-key counts, but those maps do not show which resolved step source owns each key. Adding a source-qualified companion count keeps the registry precise without exposing option values or implying execution readiness.

## What Changes

- Add additive `submit_once_bundle_step_source_option_key_counts` to `catalog validate` detailed and summary payloads.
- Add additive `pingan_bundle_step_source_option_key_counts` to `catalog validate` detailed and summary payloads.
- Keep both fields read-only and derived only from selected resolved bundle definitions.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-11 remains `[部分实现]`
- No catalog entry, task, report, trade, or bundle step execution is introduced.
