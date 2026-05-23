## Context

The runtime registry already contains:

- `buy_submit_once` audit presets under submit-once names.
- ordinary `sell` audit presets under Ping An sell names.
- command bundles that either combine a task step with a report step, or run audit diagnostics from recent failures.

After introducing `sell_submit_once`, the missing piece is runtime discoverability for that method. The new entries should be explicit enough that catalog readers can distinguish sell submit-once from default buy submit-once.

## Goals / Non-Goals

**Goals:**

- Register Ping An `sell_submit_once` daily and period report presets.
- Register command-catalog entries for exception/rejected/failed diagnostics.
- Register diagnostic bundles and task+report follow-up bundles.
- Make `catalog plan` include `side=sell` for bundle task steps that force sell submit-once.

**Non-Goals:**

- No new task implementation or trading manager behavior.
- No new free-form workflow builder.
- No generic non-PingAn `sell_submit_once` report family until another broker/method exists.
- No generated mutation of historical audit data.

## Decisions

- Use `sell-submit-once` in preset/catalog/bundle names.
  - Rationale: it mirrors `sell_submit_once` while staying readable in CLI identifiers.
- Add only Ping An-specific report presets.
  - Rationale: the implemented method is on `TdxTradeManager.pingan`; a generic method registry would overclaim.
- Add `side` to catalog key-field extraction.
  - Rationale: planned bundles with task step options should show that `task-submit-once` is being forced to sell side.

## Risks / Trade-offs

- More runtime JSON entries increase registry size -> keep the set to daily/period exception/rejected/failed and matching bundles only.
- Follow-up bundles still require caller-supplied trade fields at execution time -> catalog plan remains non-executing evidence, not proof of a successful trade.
