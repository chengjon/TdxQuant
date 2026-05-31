# Design

## Interface

Add `TdxTaskManager.pingan_live_manual_acceptance(...)` with these inputs:

- `output_path`: required JSON artifact path.
- `operator`: required operator/reviewer identifier.
- `environment`: required environment label.
- `accepted_at`: optional timestamp. If omitted, use current UTC time.
- `outcomes`: required list of operator-confirmed outcome statuses.
- `evidence_ref`: optional external reference such as ticket, runbook, screenshot bundle, or review note.
- `dry_run`: default `False`. When true, return the artifact payload and write plan without writing the file.
- `overwrite`: default `False`. When false, existing output paths are rejected.

The controlled artifact schema is the existing consumer schema:

```json
{
  "schema": "tdx.desktop_trade.pingan_live_manual_acceptance.v1",
  "operator": "ops-reviewer",
  "environment": "paper/live/manual-review",
  "accepted_at": "2026-05-31T00:00:00Z",
  "outcomes": [
    {"status": "confirmed", "accepted": true}
  ]
}
```

## Validation

The task requires all four statuses currently used by acceptance coverage: `confirmed`, `rejected`, `failed`, and `exception`. Inputs outside that set are rejected. Duplicate outcomes are normalized to one status. Missing required inputs return `ErrorCode.INVALID_REQUEST`.

## Output

The result includes `live_manual_acceptance_record` metadata:

- `schema=tdx.desktop_trade.pingan_live_manual_acceptance_record.v1`
- `artifact_schema=tdx.desktop_trade.pingan_live_manual_acceptance.v1`
- output path, dry-run/write status, overwrite flag
- covered and missing outcomes
- `execution_mode=manual_acceptance_record`
- `side_effect_level=file_write` for writes, `none` for dry-run

## Boundaries

This task records explicit operator-provided evidence. It does not validate broker state, does not run the desktop, does not submit or replay orders, and does not prove production readiness by itself. It only creates a controlled artifact that existing report and promotion readiness tasks can consume.

