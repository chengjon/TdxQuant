# Design

## Scope

This change registers a safe example manifest and a task/catalog discovery path for PingAn promotion readiness rollup. It is intentionally a registration and validation slice, not a live trading implementation slice.

## Runtime Artifacts

The sample manifest lives under `runtime/pingan/` and uses the existing manifest schema:

- `schema`: `tdx.desktop_trade.pingan_promotion_readiness_manifest.v1`
- evidence paths for preflight, dialog readiness, and acceptance coverage examples
- `max_evidence_age_seconds`
- `expected_gates`
- explanatory metadata that marks the file as example-only

The sample points to example evidence filenames only. It must not contain real account identifiers, real broker evidence, or a live acceptance claim.

## Task Preset

`runtime/task-presets.json` adds `plan-pingan-promotion-readiness`:

- `command`: `pingan-promotion-readiness-rollup`
- `profile`: `default`
- `api_profile`: `safe_read`
- `options.evidence_manifest_path`: sample manifest path

The preset intentionally omits `json_output_path` so discovery remains read-only by default. Operators may still pass explicit output arguments when they deliberately execute the task.

## Command Catalog Entry

`runtime/command-catalog.json` adds a task source entry for the preset. `catalog list` can filter it by labels such as `pingan`, `readiness`, and `manifest`. `catalog plan --entry plan-pingan-promotion-readiness` resolves the preset and returns non-execution constraints without calling `TdxTaskManager`.

## Boundary

The catalog path must stay read-only:

- `catalog plan` and `catalog list` do not execute task/report/trade/bundle steps.
- The sample manifest does not prove provider ownership, desktop lifecycle control, audit completeness, or live manual acceptance.
- `FUNCTION_TREE.md` D-07/D-08 remain `[部分实现]`.
