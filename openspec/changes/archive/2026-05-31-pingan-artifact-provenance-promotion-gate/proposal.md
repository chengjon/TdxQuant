# PingAn Artifact Provenance Promotion Gate

## Why

The PingAn promotion decision now requires source evidence schemas, but a hand-written JSON file can still include those schemas. D-07/D-08 implemented-status review should require evidence artifacts that declare where they came from, not just JSON objects that match field names.

This change adds an artifact provenance gate so complete-looking, schema-valid evidence remains blocked unless every source file carries a supported artifact provenance record.

## What Changes

- Add `artifact_provenance_status` to PingAn promotion readiness rollup output.
- Require each source evidence file to include an `artifact_provenance` object with a stable provenance schema.
- Verify source kind, producer, and evidence schema for preflight, dialog readiness, and acceptance coverage artifacts.
- Add blocked reason `unverified_artifact_provenance` to the implemented-status promotion decision.
- Update tests and `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Non-Goals

- Do not execute PingAn workflows.
- Do not generate live evidence automatically.
- Do not treat artifact provenance as production readiness.
- Do not auto-edit `FUNCTION_TREE.md` status.
- Do not promote D-07 or D-08 to `[已实现]`.
