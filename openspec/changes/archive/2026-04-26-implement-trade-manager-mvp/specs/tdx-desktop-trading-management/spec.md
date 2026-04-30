## MODIFIED Requirements

### Requirement: Desktop trading management SHALL define a dedicated top-level management path
The system SHALL reserve a dedicated top-level management path for desktop automation trading instead of routing it through query API management.

#### Scenario: Future top-level trade manager is introduced
- **WHEN** the project introduces a standardized top-level desktop trading entrypoint
- **THEN** it MUST be introduced as a dedicated trade management surface such as `TradeManager` or an equivalent trading facade

#### Scenario: Trading governance remains distinct from read-only query governance
- **WHEN** top-level management behavior is designed
- **THEN** trading-specific concerns such as window state, HID/Win32/UIA coordination, confirmation handling, and state backfill MUST remain governed by the desktop trading management capability

#### Scenario: Caller uses TradeManager for Ping An buy workflow
- **WHEN** a caller executes the stable Ping An desktop buy workflow through the top-level management layer
- **THEN** the system MUST expose that workflow through a dedicated trade manager path rather than direct attachment to `TdxApiManager`

#### Scenario: TradeManager persists trading artifacts after execution
- **WHEN** a top-level desktop trading workflow completes
- **THEN** the trading management layer MUST be able to write standardized state backfill artifacts such as last-order state or append-only event logs
