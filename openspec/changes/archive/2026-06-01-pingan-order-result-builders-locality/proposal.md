## Why

The D-07/D-08 PingAn execution seam now routes buy, sell, submit-once, and confirm-current through internal execution modules, but order-specific result construction for duplicate submissions, submission-key conflicts, and trade-risk rejections still lives as private `TdxTradeManager` helpers.

Those helpers are not manager policy; they are part of the PingAn order execution result shape. Keeping them in the manager makes the facade retain execution-module knowledge and weakens the locality gained by the previous seam work.

## What Changes

- Add PingAn order result builder helpers to `tdxquant/trade/pingan_execution.py`.
- Add a small order result context object for code/price/quantity input projection.
- Route `TdxTradeManager` order handler construction and submit-ready risk rejection through the module-level builders.
- Remove the now-redundant manager private result builder methods.
- Add direct focused tests for the new builders.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## Impact

- Behavior: unchanged public manager/CLI/task/catalog behavior.
- Risk: low; this is internal result-builder locality with focused direct tests and existing PingAn manager regression coverage.
- Boundary: no new public API, no new execution primitive, no workflow builder, no live broker readiness claim, and no production trading readiness claim.
