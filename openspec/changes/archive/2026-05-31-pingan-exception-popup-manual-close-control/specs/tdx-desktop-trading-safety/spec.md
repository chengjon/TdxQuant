## ADDED Requirements

### Requirement: PingAn exception popup control SHALL remain explicit and bounded
PingAn desktop trading SHALL expose an operator-invoked exception popup control that can inspect the current result popup and close a recognized exception-like popup only when close is explicitly confirmed.

#### Scenario: Inspect reports exception popup status without side effects
- **WHEN** `TdxTradeManager.pingan.exception_popup(...)` is called with `action=inspect`
- **THEN** the manager MUST return dialog lookup, exception lookup, and result confirm lookup evidence
- **AND** the manager MUST NOT click controls, submit orders, retry, recover, resubmit, or write trade artifacts.

#### Scenario: Close requires explicit confirmation before click
- **WHEN** `TdxTradeManager.pingan.exception_popup(...)` is called with `action=close` and `confirm_close=false`
- **THEN** the manager MUST reject the request before clicking any desktop control
- **AND** the result MUST state that close was not executed and that retry, recovery, and resubmission were not executed.

#### Scenario: Close clicks only a recognized exception popup confirm control
- **WHEN** `TdxTradeManager.pingan.exception_popup(...)` is called with `action=close`, `confirm_close=true`, an exception-like result popup is detected, and its confirm control is found
- **THEN** the manager MUST click the confirm control once through the stable dialog click helper
- **AND** the result MUST record `close_executed`, `confirm_click_executed`, `retry_executed=false`, `recovery_executed=false`, `resubmission_executed=false`, and `order_submitted=false`.

#### Scenario: Close does not close non-exception result dialogs
- **WHEN** `TdxTradeManager.pingan.exception_popup(...)` is called with `action=close`, `confirm_close=true`, and no exception-like popup text is detected
- **THEN** the manager MUST NOT click the result confirm control
- **AND** the result MUST require manual review instead of treating the dialog as handled.
