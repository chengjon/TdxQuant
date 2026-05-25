## Why

E-11 keeps `FUNCTION_TREE.md` as the single registry for task/report bundle coverage. Existing catalog validation reports task/report option-key counts, but it does not show which catalog step source owns those option keys. That leaves a small blind spot when reviewing fixed runtime bundles without executing them.

## What Changes

- Add additive `task_report_bundle_step_source_option_key_counts` to `catalog validate` detailed payloads.
- Include the same field in `catalog validate --view summary`.
- Keep the field strictly read-only and derived only from selected resolved bundles that contain both task and report steps.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-11 remains `[部分实现]`
- No task/report/trade/catalog entry or bundle step execution is introduced.
