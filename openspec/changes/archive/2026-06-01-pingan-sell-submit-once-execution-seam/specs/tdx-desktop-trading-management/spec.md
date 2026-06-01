## ADDED Requirements

### Requirement: Desktop trading management SHALL align PingAn submit-once sides behind the internal execution seam
The desktop trading management layer SHALL route both PingAn buy submit-once and sell submit-once manager paths through the internal PingAn execution seam while preserving public manager contracts, method identity, safety gates, lifecycle/broker readiness gates, audit metadata, and artifact behavior.

#### Scenario: Sell submit-once uses the internal execution seam
- **WHEN** a caller executes `TdxTradeManager.pingan.sell_submit_once(...)`
- **THEN** the manager MUST route the normalized sell submit-once request through the internal PingAn execution seam before desktop dispatch
- **AND** the public result MUST preserve existing `method=sell_submit_once` manager/audit identity and safety metadata

#### Scenario: Sell submit-once desktop primitive boundary is preserved
- **WHEN** the internal execution seam dispatches a sell submit-once request
- **THEN** the desktop dispatch MUST continue to use the existing sell desktop flow
- **AND** the system MUST NOT imply that a separate `run_pingan_sell_submit_once` desktop primitive exists
