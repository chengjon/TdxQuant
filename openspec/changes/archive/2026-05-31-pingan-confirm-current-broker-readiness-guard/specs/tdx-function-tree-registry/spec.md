## ADDED Requirements

### Requirement: D-07 confirm-current broker readiness guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register confirm-current broker readiness guard coverage as D-07 partial safety evidence without promoting PingAn trading to implemented status.

#### Scenario: D-07 registers confirm-current broker readiness guard without status promotion
- **WHEN** D-07 cites `pingan-confirm-current-broker-readiness-guard`
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade confirm-current --require-broker-readiness`, `task trade-confirm-current --require-broker-readiness`, and `TdxTradeManager.pingan.confirm_current`
- **AND** the row boundary MUST state that this is opt-in broker runtime health guard evaluation only and does not prove lifecycle control, retry/backoff/recovery, live/manual acceptance, or production trading readiness.
