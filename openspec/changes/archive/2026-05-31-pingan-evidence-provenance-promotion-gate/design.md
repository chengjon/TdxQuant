# Design

## Evidence Contract Status

`promotion_readiness_rollup` will include `evidence_contract_status`:

- `schema`: `tdx.desktop_trade.pingan_promotion_readiness_evidence_contract.v1`
- `status`: `verified` or `unverified`
- `invalid_source_kinds`: source kinds that fail contract validation
- `source_statuses`: one entry per required source kind

Each source status records:

- `source_kind`
- `source_path`
- `schema_key`
- `expected_schema`
- `observed_schema`
- `schema_valid`
- `status`
- `reason`

## Contract Rules

The contract is verified only if:

- preflight evidence contains `promotion_gate_status.schema_version` matching `tdx.desktop_trade.pingan_promotion_gate_status.v1`;
- dialog readiness evidence contains `desktop_lifecycle_gate_status.schema_version` matching `tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1`;
- acceptance coverage evidence contains `acceptance_outcome_coverage_status.schema` matching `tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`.

Missing evidence, missing schema keys, or schema mismatch mark the source as unverified.

## Promotion Decision Integration

`implemented_status_promotion_decision` adds blocked reason `unverified_evidence_contract` when `evidence_contract_status.status != verified`.

This makes complete-looking ad hoc JSON insufficient for D-07/D-08 implemented-status review.

## Boundary

The check validates source artifact contracts only. It does not prove live broker availability, UI login readiness, order safety, or production readiness by itself.
