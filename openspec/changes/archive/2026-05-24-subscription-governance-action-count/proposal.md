## Why

`FUNCTION_TREE.md` keeps B-16/E-09 subscription long-run governance as partial because the summary surface is still being hardened with explicit read-only evidence. The detailed governance payload already includes an advisory `actions` list and `action_summary.count`, while summary views expose bounded action samples.

Adding a top-level `governance.action_count` makes the action cardinality explicit and symmetrical with `reason_count`, without exposing the full actions list in summary views or changing reconnect/backoff/lifecycle behavior.

## What Changes

- Add additive `governance.action_count` to the detailed subscription watch status summary.
- Include `governance.action_count` in CLI and HTTP watch-status summary views when actions are present.
- Update tests and `FUNCTION_TREE.md` evidence/boundary for B-16/E-09.

## Non-Goals

- No new reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.
- No expansion of summary views to include full `actions`.
- No change to existing advisory action semantics or ordering.
