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

### Requirement: Desktop trading management SHALL expose a dedicated Ping An sell submit-once identity

The desktop trading management layer SHALL expose a dedicated Ping An sell submit-once manager path that preserves existing sell execution behavior while recording submit-once-specific identity.

#### Scenario: Caller runs Ping An sell submit-once through the trade manager

- **WHEN** a caller executes `TdxTradeManager.pingan.sell_submit_once`
- **THEN** the manager MUST reuse the existing Ping An sell desktop execution flow
- **AND** the result metadata MUST record the manager method as `sell_submit_once`
- **AND** idempotency and safety controls such as `submission_key` and `max_price` MUST continue to apply before desktop execution

#### Scenario: Caller inspects sell submit-once boundaries

- **WHEN** a caller uses the dedicated sell submit-once manager path
- **THEN** the system MUST NOT imply a separate `run_pingan_sell_submit_once` desktop primitive exists
- **AND** the boundary MUST remain limited to the existing Ping An sell desktop workflow

### Requirement: Desktop trading management SHALL distinguish broker validation boundaries

The desktop trading management layer SHALL distinguish PingAn validated desktop execution from TongDaXin trading probe boundaries when adopting external merge evidence.

#### Scenario: PingAn mixed-chain buy loop is accepted
- **WHEN** PingAn validation evidence from the external `tdx` tree is adopted
- **THEN** desktop trading documentation and registry entries MUST state that the accepted execution path uses UIA field entry, HID first confirmation trigger, Win32 confirmation command, and HID result close
- **AND** the accepted boundary MUST include the requirement that the desktop returns to a next-order-ready state before continued operation

#### Scenario: PingAn execution is not represented as pure nonphysical Win32 submission
- **WHEN** documentation describes the accepted PingAn execution path
- **THEN** it MUST NOT claim that pure Win32 or pure UIA message submission alone completed the final trading loop

#### Scenario: TongDaXin trading evidence remains separate
- **WHEN** documentation describes TongDaXin trading bridge behavior
- **THEN** it MUST NOT inherit PingAn execution status
- **AND** it MUST retain its own evidenced boundary

### Requirement: Desktop trading management SHALL preserve current trade governance during merge

The merge SHALL preserve existing desktop trade safety, ledger, audit, and compatibility-governance behavior while adopting external `tdx` evidence.

#### Scenario: Merge updates docs or registry
- **WHEN** implementation updates desktop trading documentation or registry status
- **THEN** existing stable trade manager, trade service, submission ledger, and trade audit behavior MUST remain unchanged unless an explicit implementation task modifies them

#### Scenario: Focused trade verification runs
- **WHEN** desktop trading merge changes are applied
- **THEN** focused verification MUST include existing PingAn trade manager or gateway tests where local execution does not require a live client

