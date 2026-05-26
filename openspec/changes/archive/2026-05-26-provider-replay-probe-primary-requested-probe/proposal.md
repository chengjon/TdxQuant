# Proposal: Provider Replay Primary Requested Probe

## Why

Provider replay probe summaries already expose requested, healthy, failed, and not-requested target lists plus primary healthy/failed/not-requested hints. There is no compact hint for the first explicitly requested probe, so callers must inspect the full `requested` list when they only need a stable representative target.

## What Changes

- Add read-only `runtime.probe_summary.primary_requested_probe`.
- Derive the value from the first item in the existing `requested` list, or `null` when no probe was requested.
- Cover detailed provider replay status and the CLI summary view, which copies the same `probe_summary`.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` evidence/boundary.

## Non-Goals

- Do not request additional probes or change `--probe-*` / `--probe-all` behavior.
- Do not change probe ordering, health status classification, or reachability classification.
- Do not start sockets, manage daemon lifecycle, mutate providers, or imply endpoint coverage/readiness.
