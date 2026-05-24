# Proposal: Provider Replay Probe Unhealthy Count

## Why

`runtime.probe_summary` already exposes an `unhealthy` target list and a legacy `failed_count`, but consumers have to rely on the differently named failed count to compare against the unhealthy list. A derived `unhealthy_count` makes the replay status payload internally consistent without changing probe behavior.

## What Changes

- Add `runtime.probe_summary.unhealthy_count` to provider replay status.
- Derive it from the existing unhealthy probe target list.
- Preserve `failed_count`, status counts, probe target lists, summary views, and daemon lifecycle boundaries.

## Out Of Scope

- No new probe target, probe request flag, socket startup, daemon management, restart/backoff policy, or live market session behavior.

## Success Criteria

- Detailed status reports `probe_summary.unhealthy_count`.
- `unhealthy_count` equals `len(probe_summary.unhealthy)` and remains equal to `failed_count`.
- Summary view preserves the same `probe_summary.unhealthy_count`.
