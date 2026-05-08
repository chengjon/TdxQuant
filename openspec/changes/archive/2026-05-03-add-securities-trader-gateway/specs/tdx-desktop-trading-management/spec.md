## ADDED Requirements

### Requirement: Desktop trading management SHALL expose a parallel securities trade service
The system SHALL expose a broker-neutral securities trade service and gateway registry in parallel with the existing desktop trade manager path.

#### Scenario: Caller resolves a canonical securities trade path
- **WHEN** a caller executes first-phase canonical securities trading behavior
- **THEN** the system MUST route the request through a dedicated securities trade service and gateway resolution path
- **AND** that path MUST remain parallel to the legacy `TdxTradeManager.pingan.*` workflow surface

#### Scenario: Management resolves the first-phase PingAn desktop gateway
- **WHEN** a caller selects the first-phase PingAn desktop broker for canonical order placement
- **THEN** the management layer MUST resolve a dedicated PingAn desktop trader gateway implementation
- **AND** the canonical service MUST govern lifecycle, storage, and capability reporting around that implementation

### Requirement: Desktop trading management SHALL persist canonical trader artifacts alongside legacy PingAn artifacts during migration
The system SHALL persist canonical securities trader artifacts during first-phase gateway execution without requiring immediate removal of the existing PingAn runtime artifacts.

#### Scenario: Canonical gateway execution writes canonical trader storage
- **WHEN** a first-phase order executes through the canonical securities trade service
- **THEN** the management layer MUST write canonical trader artifacts for order events, order snapshots, or trade fills under the dedicated trader storage area

#### Scenario: Migration keeps legacy PingAn artifacts available
- **WHEN** the system introduces canonical trader storage
- **THEN** existing PingAn runtime artifacts such as submission ledger, last-order state, and trade-audit outputs MUST remain available during the migration period
- **AND** the introduction of canonical storage MUST NOT require immediate deprecation of the legacy artifact paths

### Requirement: Desktop trading management SHALL preserve TdxTradeManager as a compatibility surface during migration
The system SHALL preserve the existing top-level desktop trade manager surface while the canonical securities trade service is being introduced.

#### Scenario: Existing PingAn workflow surface remains callable
- **WHEN** existing callers execute the legacy PingAn desktop trade manager workflows during the migration period
- **THEN** those workflows MUST remain callable through their current surface
- **AND** the implementation MAY satisfy them through delegation into the canonical trade service where the caller contract remains equivalent

#### Scenario: Canonical service does not force immediate removal of boundary workflows
- **WHEN** the project introduces the canonical securities trade service
- **THEN** desktop boundary workflows such as submit-ready and confirm-current MUST remain governed by the desktop trading management capability
- **AND** they MUST NOT be required to masquerade as broker-neutral canonical order states
