# Design: Catalog Trade Plan Input Coverage Status

## Status Model

`trade_plan_boundary.input_coverage_status` is derived from the existing required/provided/missing input field lists:

- `no_required_inputs`: the trade command has no required input fields.
- `complete`: all required fields are provided by resolved preset/options.
- `missing_required_inputs`: one or more required fields are absent.

The field is intentionally named as input coverage, not readiness. It does not evaluate account state, broker connectivity, safety policy, order validity, dialog readiness, or dispatch execution.

## Implementation

Add a small helper near `_build_catalog_trade_plan_boundary()` to keep the state derivation explicit and reusable inside the boundary builder. The builder will keep returning the existing lists and count fields and append `input_coverage_status`.

## Testing

Add focused catalog summary tests for:

- A trade entry with missing order fields.
- A trade entry with all required order fields provided.
- A confirm-current entry with no required order inputs.

These tests exercise real CLI parsing and catalog planning paths without executing dispatch.
