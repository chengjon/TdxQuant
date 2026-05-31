## ADDED Requirements

### Requirement: Guarded trade-buy CLI SHALL accept lifecycle owner-lock guard options

The stable `task guarded-trade-buy` CLI SHALL expose optional lifecycle owner-lock guard arguments.

#### Scenario: Guarded trade-buy parses owner-lock guard options

- **WHEN** a caller parses `task guarded-trade-buy --require-lifecycle-owner-lock`
- **THEN** the parsed arguments MUST include lifecycle statefile path, lifecycle owner token, stale timeout, and require flag fields.

#### Scenario: Guarded trade-buy dispatch forwards owner-lock guard options

- **WHEN** task CLI dispatch handles `guarded-trade-buy`
- **THEN** it MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTaskManager.guarded_trade_buy(...)`.
