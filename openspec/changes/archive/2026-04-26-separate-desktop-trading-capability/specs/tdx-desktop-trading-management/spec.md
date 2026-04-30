## ADDED Requirements

### Requirement: Desktop trading management SHALL exist as a capability parallel to query API management
The system SHALL define desktop automation trading as an independent capability instead of treating it as an extension of query API management.

#### Scenario: Project architecture distinguishes query and trading governance
- **WHEN** the project documents or code structure describe top-level capabilities
- **THEN** desktop automation trading MUST be represented as a capability parallel to `tdx-api-management`

#### Scenario: Desktop trading is not attached to TdxApiManager
- **WHEN** a caller needs to execute desktop automation trading behavior
- **THEN** that behavior MUST NOT be modeled as a method added onto `TdxApiManager`

### Requirement: Desktop trading management SHALL preserve existing production trading flows during capability separation
The system SHALL keep the current production desktop trading flows usable while the capability boundary is formalized.

#### Scenario: Existing flat trading commands remain usable
- **WHEN** the desktop trading capability is formally introduced
- **THEN** existing commands such as `pingan-buy-submit-once` and `pingan-buy` MUST remain available during the migration period

#### Scenario: Existing desktop modules remain valid implementation anchors
- **WHEN** the capability boundary is documented
- **THEN** the current `tdxquant/desktop/`, `tdxquant/brokers/`, and related runtime/CLI paths MUST remain valid implementation anchors rather than being deprecated immediately

### Requirement: Desktop trading management SHALL define a dedicated top-level management path
The system SHALL reserve a dedicated top-level management path for desktop automation trading instead of routing it through query API management.

#### Scenario: Future top-level trade manager is introduced
- **WHEN** the project introduces a standardized top-level desktop trading entrypoint
- **THEN** it MUST be introduced as a dedicated trade management surface such as `TradeManager` or an equivalent trading facade

#### Scenario: Trading governance remains distinct from read-only query governance
- **WHEN** top-level management behavior is designed
- **THEN** trading-specific concerns such as window state, HID/Win32/UIA coordination, confirmation handling, and state backfill MUST remain governed by the desktop trading management capability
