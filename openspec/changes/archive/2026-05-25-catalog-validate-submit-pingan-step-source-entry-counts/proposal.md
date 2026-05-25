## Why

E-11 catalog validation reports submit-once and PingAn step entry counts, but those maps are not source-qualified. Adding `source:entry` counts improves auditability of fixed runtime bundle definitions without exposing full manifests or implying execution readiness.

## What Changes

- Add additive `submit_once_bundle_step_source_entry_counts` to `catalog validate` detailed and summary payloads.
- Add additive `pingan_bundle_step_source_entry_counts` to `catalog validate` detailed and summary payloads.
- Keep both fields read-only and derived only from selected resolved bundle definitions.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-11 remains `[部分实现]`
- No catalog entry, task, report, trade, or bundle step execution is introduced.
