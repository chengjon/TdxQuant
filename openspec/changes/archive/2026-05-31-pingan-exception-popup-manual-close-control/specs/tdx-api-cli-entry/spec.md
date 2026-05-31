## ADDED Requirements

### Requirement: Trade CLI SHALL expose PingAn exception popup control
The stable trade CLI SHALL expose an exception popup inspect/close entrypoint and forward it to the PingAn manager without executing order workflows.

#### Scenario: CLI forwards readonly inspect arguments
- **WHEN** a caller runs `trade exception-popup --action inspect` with dialog lookup and timeout options
- **THEN** the CLI MUST pass those values to `TdxTradeManager.pingan.exception_popup(...)`
- **AND** the CLI MUST NOT dispatch task, catalog, report, buy/sell, submit-ready, submit-once, or confirm-current workflow steps.

#### Scenario: CLI forwards confirmed close arguments
- **WHEN** a caller runs `trade exception-popup --action close --confirm-close`
- **THEN** the CLI MUST forward `action=close` and `confirm_close=true` to `TdxTradeManager.pingan.exception_popup(...)`
- **AND** the CLI MUST NOT retry, recover, resubmit, acquire lifecycle ownership, or manage the PingAn process lifecycle directly.
