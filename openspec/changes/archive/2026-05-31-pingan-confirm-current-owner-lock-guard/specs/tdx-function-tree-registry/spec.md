## ADDED Requirements

### Requirement: D-07 confirm-current owner-lock guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register confirm-current owner-lock guard coverage as D-07 partial safety evidence without promoting PingAn trading to implemented status.

#### Scenario: D-07 registers confirm-current owner-lock guard without status promotion
- **WHEN** D-07 cites `pingan-confirm-current-owner-lock-guard`
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade confirm-current --require-lifecycle-owner-lock`, `task trade-confirm-current --require-lifecycle-owner-lock`, and `TdxTradeManager.pingan.confirm_current`
- **AND** the row boundary MUST state that this is opt-in owner-lock guard evaluation only and does not prove lifecycle control, broker readiness, live/manual acceptance, or production trading readiness.
