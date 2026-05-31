# Design: PingAn promotion readiness evidence freshness gate

## Overview

The rollup task already reads JSON evidence from three sources:

- preflight evidence
- dialog readiness evidence
- acceptance coverage evidence

This change adds an optional freshness threshold in seconds. When the threshold is provided, the task will compare each evidence file's modification time with the current clock. Evidence older than the threshold is marked stale and that gate remains incomplete.

## Data Model

The rollup will add:

- `evidence_freshness_cutoff_seconds`
- `evidence_freshness_status`
- `stale_evidence_kinds`
- `stale_evidence_paths`

Each source entry will also record a freshness status such as:

- `fresh`
- `stale`
- `missing`
- `unreadable`

## Behavior

- If no freshness cutoff is provided, the rollup behaves as before.
- If a cutoff is provided, each evidence path must be checked independently.
- Stale evidence must not be counted as complete even if its JSON payload still says ready/complete.
- Read-only behavior remains unchanged: the task never executes workflow steps, broker operations, or desktop actions.

## Boundary

This is a guardrail on evidence interpretation, not a new readiness signal. It prevents stale files from being mistaken for current state, but it does not prove actual production readiness or implemented status.

