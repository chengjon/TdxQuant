## ADDED Requirements

### Requirement: Desktop trading management SHALL route ordinary PingAn sell through the internal execution seam
The desktop trading management layer SHALL route ordinary `TdxTradeManager.pingan.sell(...)` execution through the internal PingAn execution seam while preserving the public manager contract, method identity, idempotency handling, safety gates, lifecycle/broker readiness gates, desktop dispatch behavior, audit metadata, and artifact behavior.

#### Scenario: Ordinary sell uses the internal execution seam

- **WHEN** a caller executes `TdxTradeManager.pingan.sell(...)`
- **THEN** the manager MUST route the normalized sell request through the internal PingAn execution seam before desktop dispatch
- **AND** the normalized request MUST preserve `method=sell`, timing label `pingan.sell`, code, price, quantity, submission key, max price, and effective profile options
- **AND** the public result MUST preserve existing audit, idempotency, safety, lifecycle, and artifact fields

#### Scenario: Ordinary sell desktop primitive boundary is preserved

- **WHEN** the internal execution seam dispatches an ordinary sell request
- **THEN** the desktop dispatch MUST continue to use the existing `run_pingan_sell_fast` flow with the existing argument set
- **AND** the system MUST NOT introduce a new public command, catalog entry, task preset, workflow builder, or desktop primitive for ordinary sell seam routing

