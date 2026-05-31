# Design: PingAn promotion readiness manifest input

## Manifest Shape

The manifest is a JSON object with schema:

`tdx.desktop_trade.pingan_promotion_readiness_manifest.v1`

It may include:

- `preflight_path`
- `dialog_readiness_path`
- `acceptance_coverage_path`
- `max_evidence_age_seconds`
- `expected_gates`

`expected_gates` is informational: the rollup reports any mismatch as manifest metadata, but it does not execute additional checks or workflows.

## Resolution Rules

The task resolves input values in this order:

1. Load manifest values when `evidence_manifest_path` is provided.
2. Apply explicit task/CLI arguments as overrides.
3. Build the existing read-only rollup from the resolved values.

The output includes `evidence_manifest` with schema, path, loaded flag, expected gate names, and any missing expected gates.

## Boundary

The manifest is an audit aid, not an execution plan. It does not refresh evidence, does not validate live broker state, and does not prove production readiness. It only stabilizes which existing evidence artifacts are read by the already non-executing rollup.

