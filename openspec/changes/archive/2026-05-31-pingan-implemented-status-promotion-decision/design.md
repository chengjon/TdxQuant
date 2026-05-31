# Design

## Decision Shape

`promotion_readiness_rollup` will include `implemented_status_promotion_decision`:

- `schema`: stable decision schema.
- `target_nodes`: `["D-07", "D-08"]`.
- `decision`: `eligible_for_review` or `blocked`.
- `implemented_status_eligible`: boolean.
- `required_gates`: PingAn readiness gate order.
- `completed_gates` and `incomplete_gates`.
- `blocked_reasons`: stable reason codes.
- `source_errors`, `missing_evidence_kinds`, `stale_evidence_kinds`, and `stale_evidence_paths`.
- `sample_manifest`: boolean.
- `manual_status_review_required`: always true.
- `function_tree_status_transition_executed`: always false.
- `boundary`: explicit non-execution and non-production-readiness statement.

## Eligibility Rules

The decision is eligible only when all of the following are true:

- every required gate is complete;
- there are no missing evidence kinds;
- there are no source errors;
- there is no stale evidence;
- no expected gates are missing from the rollup gate map;
- the manifest is not marked example/sample-only.

Any failure produces `decision=blocked` and adds stable blocked reason codes:

- `incomplete_required_gates`
- `missing_evidence`
- `source_errors`
- `stale_evidence`
- `missing_expected_gates`
- `sample_manifest`

## Manifest Handling

The manifest loader will copy example/sample metadata into manifest status when present:

- `example_only`
- `sample_only`

The runtime sample manifest remains useful for discovery, but it can never satisfy implemented-status promotion eligibility.

## Boundary

The decision is still read-only. It does not run PingAn trading paths and does not edit `FUNCTION_TREE.md`. A later explicit status-transition change must review real environment evidence before D-07/D-08 can be changed to `[已实现]`.
