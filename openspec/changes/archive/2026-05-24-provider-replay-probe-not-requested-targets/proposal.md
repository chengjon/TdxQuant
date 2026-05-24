# Proposal: Provider Replay Probe Not Requested Targets

## Why

Provider replay status already exposes probe `requested`, `healthy`, and `unhealthy` target lists plus `not_requested_count`. Consumers can see how many probes were skipped, but they must infer which specific probe targets were not requested.

The replay provider summary should make skipped probe targets explicit while preserving the read-only probe boundary.

## What Changes

- Add `probe_summary.not_requested` as an ordered list of probe target names whose status is `not_requested`.
- Surface the same rollup through existing `provider-replay status --view summary`, which already deep-copies `probe_summary`.
- Keep probe execution opt-in and keep daemon lifecycle behavior unchanged.

## Non-Goals

- Do not start sockets, manage daemon lifecycle, or add restart/backoff behavior.
- Do not probe targets unless the existing explicit probe flags request them.
- Do not replace individual probe evidence with the aggregate summary.
