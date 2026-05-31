## ADDED Requirements

### Requirement: D-08 submit-once broker readiness guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register submit-once broker readiness guard coverage as D-08 partial safety evidence without promoting PingAn submit-once to implemented status.

#### Scenario: D-08 registers submit-once broker readiness guard without status promotion
- **WHEN** D-08 cites `pingan-submit-once-broker-readiness-guard`
- **THEN** D-08 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade submit-once --require-broker-readiness`, `task trade-submit-once --require-broker-readiness`, and `TdxTradeManager.pingan.buy_submit_once/sell_submit_once`
- **AND** the row boundary MUST state that this is opt-in broker runtime health guard evaluation only and does not prove lifecycle control, retry/backoff/recovery, live/manual acceptance, or production trading readiness.
