## Why

E-11 catalog validation reports submit-once and PingAn bundle counts plus several per-step aggregate maps, but callers must currently infer each subset's total step count by summing a map. Explicit step counts make the registry summary easier to audit while staying non-executing.

## What Changes

- Add additive `submit_once_bundle_step_count` to `catalog validate` detailed and summary payloads.
- Add additive `pingan_bundle_step_count` to `catalog validate` detailed and summary payloads.
- Keep both fields read-only and derived only from selected resolved bundle definitions.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-11 remains `[部分实现]`
- No catalog entry, task, report, trade, or bundle step execution is introduced.
