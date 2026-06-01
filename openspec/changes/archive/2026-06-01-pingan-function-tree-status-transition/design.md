# Design

## Scope

This change executes the already-implemented guarded status transition. It does not add new PingAn runtime capabilities.

## Evidence Chain

1. A repository-local review packet records that D-07/D-08 gates are ready for manual implemented-status review.
2. `TdxTaskManager.pingan_implemented_status_review_result` records an approved manual review result.
3. `TdxTaskManager.pingan_implemented_status_transition_gate` validates the review result into an eligible transition gate.
4. `TdxTaskManager.pingan_implemented_status_transition` applies the status transition to `FUNCTION_TREE.md` and writes a transition record.

## Boundaries

- The transition changes only `FUNCTION_TREE.md` status cells and writes JSON evidence artifacts.
- The transition does not execute PingAn workflows, submit orders, control desktop windows, or run catalog bundles.
- Earlier evidence slices may still state that they individually did not prove implemented status; the transition record is the final evidence that authorizes the registry status change.
