## Context

`task trade-submit-once` already supports `--side buy` and defaults to buy when the option is omitted. Runtime catalog currently exposes:

- `task-submit-once` mapped to `submit-once-default`.
- `task-sell-submit-once` mapped to `sell-submit-once-default`.
- submit-once follow-up bundles whose trade step uses `task-submit-once`.

The missing piece is an explicit buy-scoped task entry that mirrors the sell-scoped entry and makes side intent visible to catalog users.

## Design

Add a new preset:

- `buy-submit-once-default`
- `command=trade-submit-once`
- same operational options as `submit-once-default`
- explicit `options.side=buy`

Add a catalog entry:

- `task-buy-submit-once`
- `source=task`
- `preset=buy-submit-once-default`
- labels include `buy-submit-once`

Add buy-scoped follow-up bundles:

- `buy-submit-once-pingan-exception-review`
- `buy-submit-once-pingan-rejection-review`
- `buy-submit-once-pingan-failure-review`

Each bundle will use `task-buy-submit-once` as the trade step and existing PingAn buy submit-once audit entries for the audit step. This is catalog composition only; it does not alter `TdxTradeManager`, gateway behavior, or desktop automation.

## Boundaries

- No new desktop trader primitive is introduced.
- The existing `submit-once-default` remains for backward compatibility.
- Real execution still requires explicit runtime parameters and the existing safety constraints.
- The bundles only plan/compose existing task and report entries.
