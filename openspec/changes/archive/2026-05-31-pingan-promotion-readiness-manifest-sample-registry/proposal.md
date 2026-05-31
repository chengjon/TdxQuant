# PingAn Promotion Readiness Manifest Sample Registry

## Why

The PingAn promotion readiness rollup can already consume explicit evidence paths and a manifest, but there is no stable, safe, discoverable sample that teaches operators how the manifest is wired through task presets and the command catalog.

Without a registered sample, `FUNCTION_TREE.md` can cite the manifest loader implementation, but readers cannot distinguish a reusable read-only discovery entry from ad hoc local files. The next slice should add a catalog/task registration point that remains strictly non-executing and does not claim production readiness.

## What Changes

- Add a sample PingAn promotion readiness evidence manifest under `runtime/`.
- Add a read-only task preset that points at the sample manifest.
- Add a command catalog entry so `catalog list` and `catalog plan` can discover and inspect the preset without executing the task workflow.
- Add tests for task preset resolution and catalog list/plan behavior.
- Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary while keeping both nodes `[部分实现]`.

## Non-Goals

- Do not execute PingAn buy/sell/submit/confirm workflows.
- Do not refresh or synthesize provider, desktop, audit, or acceptance evidence.
- Do not write readiness artifacts by default from the sample preset.
- Do not promote D-07/D-08 to `[已实现]`.
- Do not claim broker readiness, production readiness, or live trading acceptance.
