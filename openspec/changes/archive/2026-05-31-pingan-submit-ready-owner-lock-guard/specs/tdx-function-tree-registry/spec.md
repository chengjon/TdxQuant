## ADDED Requirements

### Requirement: D-07 submit-ready owner-lock guard evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register submit-ready owner-lock guard coverage as D-07 partial safety evidence without promoting PingAn trading to implemented status.

#### Scenario: D-07 registers submit-ready owner-lock guard without status promotion
- **WHEN** D-07 cites `pingan-submit-ready-owner-lock-guard`
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade submit-ready --require-lifecycle-owner-lock`, `task trade-submit-ready --require-lifecycle-owner-lock`, and `TdxTradeManager.pingan.submit_ready`
- **AND** the row boundary MUST state that this is opt-in owner-lock guard evaluation only and does not prove lifecycle control, broker readiness, live/manual acceptance, or production trading readiness.
