## Context

`trade acceptance-evidence` is now a read-only trade command. Existing PingAn diagnostics such as `trade-health-pingan-readiness`, `trade-preflight-pingan-readiness`, and `broker-capabilities` are discoverable through `runtime/command-catalog.json` and backed by trade presets.

This change follows that pattern for D-13.

## Goals / Non-Goals

Goals:

- Add an `acceptance-evidence-default` trade preset.
- Add a `trade-acceptance-evidence` command catalog entry.
- Make `catalog list --kind entry --label acceptance` find the entry.
- Make `catalog plan --entry trade-acceptance-evidence --view summary` resolve to the `acceptance-evidence` trade command without dispatch.

Non-goals:

- Do not execute `trade acceptance-evidence` from catalog plan/list.
- Do not run broker health, preflight, UIA, HID, process lifecycle, task/report, or bundle workflows.
- Do not evaluate live/manual acceptance artifacts or alter FUNCTION_TREE status.

## Design

The preset is a normal trade preset:

- `command`: `acceptance-evidence`
- `profile`: `balanced`
- `title_key`: `平安证券`
- `options.broker`: `pingan_desktop`

The catalog entry uses `source=trade`, points at the preset, and carries labels such as `trade`, `pingan`, `acceptance`, `evidence`, `readonly`, and `diagnostics`.

If the existing catalog plan boundary does not classify `acceptance-evidence`, extend it as a no-required-input diagnostics/review boundary with `execution_mode=non_executing_catalog_plan`.

## Verification

- Red tests for list and plan.
- Focused `tests/test_api_cli.py`.
- `openspec validate --all --strict`.
- `git diff --check`.
- `python scripts/validate_function_tree_registry.py`.
