# Proposal: Provider Replay Probe Total Count

## Why

`runtime.probe_summary` exposes requested, healthy, failed, and not-requested probe counts, but consumers still need to infer the total supported probe surface from implementation knowledge. A derived `total_count` makes the replay status payload self-describing without starting sockets or changing probe behavior.

## What Changes

Add `runtime.probe_summary.total_count`, derived from the fixed provider replay status probe key list. Because the provider replay status summary view copies `probe_summary`, the same scalar is available there as read-only projection data.

## Out Of Scope

- No new probe target.
- No automatic probing.
- No daemon lifecycle, scheduler, restart, or live market session support.
- No change to existing individual probe objects.

## Success Criteria

- Detailed status reports `probe_summary.total_count`.
- `requested_count + not_requested_count` equals `total_count`.
- Summary view preserves the same `probe_summary.total_count`.
