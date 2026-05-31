## ADDED Requirements

### Requirement: PingAn desktop gateway SHALL forward lifecycle owner-lock guard options

The PingAn desktop securities trader gateway SHALL forward lifecycle owner-lock requirement options to the underlying PingAn manager execution method.

#### Scenario: Gateway forwards guard options for buy/sell/submit-once

- **WHEN** `PingAnDesktopTraderGateway.place_order(...)` dispatches buy, sell, buy-submit-once, or sell-submit-once
- **THEN** it MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to the selected manager method.
