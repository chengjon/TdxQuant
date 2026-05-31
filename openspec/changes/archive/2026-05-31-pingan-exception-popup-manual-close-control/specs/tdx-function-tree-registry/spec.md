## ADDED Requirements

### Requirement: D-07/D-08 exception popup control evidence SHALL remain partial
`FUNCTION_TREE.md` SHALL register PingAn exception popup manual close control as D-07/D-08 partial desktop lifecycle evidence without promoting either node to implemented status.

#### Scenario: Registry cites exception popup manual close control without status promotion
- **WHEN** D-07 or D-08 cites `pingan-exception-popup-manual-close-control`
- **THEN** the row MUST remain `[部分实现]`
- **AND** the row MUST cite `TdxTradeManager.pingan.exception_popup`, `trade exception-popup --action inspect`, and `trade exception-popup --action close --confirm-close`
- **AND** the row boundary MUST state that the control is explicit exception-popup inspect/close only and does not retry, recover, resubmit, prove broker readiness/live acceptance, or complete workflow/lifecycle governance.
