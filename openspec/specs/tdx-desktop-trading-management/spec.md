# tdx-desktop-trading-management Specification

## Purpose

定义与查询 API 主线并行的桌面自动化交易管理能力，包括独立的顶层治理边界、稳定交易入口和标准化交易状态回填能力。
## Requirements
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

#### Scenario: Caller uses TradeManager for Ping An buy workflow
- **WHEN** a caller executes the stable Ping An desktop buy workflow through the top-level management layer
- **THEN** the system MUST expose that workflow through a dedicated trade manager path rather than direct attachment to `TdxApiManager`

#### Scenario: TradeManager persists trading artifacts after execution
- **WHEN** a top-level desktop trading workflow completes
- **THEN** the trading management layer MUST be able to write standardized state backfill artifacts such as last-order state or append-only event logs

### Requirement: Desktop trading management SHALL preserve trade safety context in persisted artifacts
The system SHALL persist normalized trade safety context into the existing last-order state and append-only event artifacts for stable desktop trading workflows.

#### Scenario: Trade manager writes safety-aware artifacts
- **WHEN** a stable desktop trade workflow finishes through `TdxTradeManager`
- **THEN** the written last-order state payload and append-only event row MUST include the normalized trade safety summary

### Requirement: Desktop trading management SHALL accept caller safety controls for stable buy workflows
The system SHALL allow stable desktop buy workflows to accept caller safety controls without breaking existing production trade flows.

#### Scenario: Caller supplies safety controls to stable desktop buy workflow
- **WHEN** a caller executes a stable desktop buy workflow through the top-level trade manager and supplies `submission_key` or `max_price`
- **THEN** the workflow MUST accept those options
- **AND** existing required trade inputs and production flow behavior MUST remain unchanged

### Requirement: Desktop trading management SHALL expose submission-ledger artifacts for keyed stable workflows
The system SHALL expose the durable submission-ledger artifact path for keyed stable desktop trade workflows.

#### Scenario: Keyed trade result exposes ledger artifact path
- **WHEN** a keyed stable desktop trade workflow finishes through `TdxTradeManager`
- **THEN** the result artifacts MUST expose the durable submission-ledger path

### Requirement: Desktop trading management SHALL consult the submission ledger before stable desktop execution
The system SHALL consult the durable submission ledger before executing a keyed stable desktop trade workflow.

#### Scenario: Submission ledger prevents duplicate desktop execution
- **WHEN** a keyed stable desktop trade workflow is invoked
- **THEN** the management layer MUST consult the current submission ledger before desktop execution
- **AND** the management layer MUST apply duplicate-short-circuit or conflicting-key rejection behavior when the ledger requires it

### Requirement: Desktop trading management SHALL expose trade-audit target discovery together with existing artifact governance
The system SHALL expose the configured trade-audit artifact target alongside the existing state, event-log, and submission-ledger artifact targets.

#### Scenario: Trade readiness summary includes trade-audit target
- **WHEN** a caller executes a stable trade discovery-style workflow such as health, preflight, or dialog readiness
- **THEN** the returned artifact target summary MUST include the configured trade-audit target path in addition to the existing trade artifact targets

### Requirement: Desktop trading management SHALL preserve audit correlation in persisted artifacts
The system SHALL preserve normalized trade-audit correlation data across the existing state and event artifacts for finalized stable trade workflows.

#### Scenario: Finalized trade writes audit-aware persisted artifacts
- **WHEN** a stable desktop trade workflow finishes through the finalized persistence path
- **THEN** the written last-order state payload MUST include the normalized `trade_audit` summary
- **AND** the appended order-event row MUST include the normalized `trade_audit` summary

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

### Requirement: Desktop trading management SHALL define PingAn plus HID as the active live-trading execution mainline
The system SHALL treat `PingAn` desktop execution with HID-backed final submit actions as the only active live-trading mainline for desktop trading workflows.

#### Scenario: Live-trading scope excludes TongDaXin execution
- **WHEN** the project defines the current live desktop trading path
- **THEN** the active execution baseline MUST be `PingAn` desktop plus HID
- **AND** `TongDaXin` trading MUST NOT be required for live execution closure

#### Scenario: PingAn live workflow persists through the standard finalized path
- **WHEN** a stable `PingAn` live trade completes through the management layer
- **THEN** the workflow MUST continue to use the standard finalized persistence path for audit, state, and event artifacts

### Requirement: Desktop trading management SHALL expose stable PingAn sell workflows alongside existing buy workflows
The system SHALL expose stable `PingAn` sell workflows that mirror the current buy workflows across both the fast path and the full submit-once path.

#### Scenario: Caller executes fast sell through the management layer
- **WHEN** a caller requests a stable `PingAn` sell workflow through the desktop trading management path
- **THEN** the system MUST support a finalized sell execution path analogous to the existing stable buy path

#### Scenario: Caller executes sell submit-once through the management layer
- **WHEN** a caller requests a stable `PingAn` sell workflow that advances through HID submit, confirmation, and result dialog handling
- **THEN** the system MUST support a finalized `sell_submit_once` execution path
- **AND** that workflow MUST preserve the same safety controls and finalized artifact governance already used by the existing buy submit-once path
