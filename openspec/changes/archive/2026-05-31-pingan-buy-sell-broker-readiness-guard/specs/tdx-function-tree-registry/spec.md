## ADDED Requirements

### Requirement: D-07 buy/sell broker readiness guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register buy/sell broker readiness guard coverage as D-07 partial safety evidence without promoting PingAn trading to implemented status.

#### Scenario: D-07 registers buy/sell broker readiness guard without status promotion
- **WHEN** D-07 cites `pingan-buy-sell-broker-readiness-guard`
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade buy --require-broker-readiness`, `trade sell --require-broker-readiness`, `task trade-buy --require-broker-readiness`, `task trade-sell --require-broker-readiness`, and `TdxTradeManager.pingan.buy/sell`
- **AND** the row boundary MUST state that this is opt-in broker runtime health guard evaluation only and does not prove lifecycle control, retry/backoff/recovery, live/manual acceptance, or production trading readiness.
