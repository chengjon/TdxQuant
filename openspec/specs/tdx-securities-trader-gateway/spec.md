# tdx-securities-trader-gateway Specification

## Purpose

定义 broker-neutral 的 A 股证券交易网关能力，包括统一下单入口、canonical 生命周期、订单/成交持久化和本地查询恢复边界。

## Requirements
### Requirement: Securities trader gateway SHALL provide a broker-neutral A-share limit-order entrypoint
The system SHALL expose a broker-neutral securities trader gateway that accepts ordinary A-share cash limit orders for both `buy` and `sell`.

#### Scenario: Caller places a buy order through the canonical gateway
- **WHEN** a caller submits a canonical securities order request with `side=buy`, ordinary A-share spot fields, and `order_type=limit`
- **THEN** the system MUST validate the request through the canonical trader gateway path
- **AND** the system MUST dispatch the request through the resolved broker adapter instead of a `buy-only` management method

#### Scenario: Caller places a sell order through the canonical gateway
- **WHEN** a caller submits a canonical securities order request with `side=sell`, ordinary A-share spot fields, and `order_type=limit`
- **THEN** the system MUST process the request through the same canonical gateway path used for buy orders
- **AND** the system MUST preserve the order side in the persisted canonical request and result artifacts

#### Scenario: Unsupported instrument or order style is rejected
- **WHEN** a caller submits a request outside the first-phase scope, such as non-A-share instruments or non-limit order styles
- **THEN** the canonical gateway MUST reject the request with an invalid-request style result
- **AND** the rejection MUST occur before live desktop execution starts

### Requirement: Securities trader gateway SHALL maintain canonical order lifecycle state
The system SHALL persist canonical order lifecycle state that is independent from desktop-specific boundary labels.

#### Scenario: Canonical order state advances through submission lifecycle
- **WHEN** a first-phase order is accepted for execution through the canonical gateway
- **THEN** the system MUST record canonical lifecycle progression using normalized states such as `CREATED`, `VALIDATED`, `SUBMITTING`, and a finalized status
- **AND** the recorded lifecycle MUST not require callers to interpret PingAn-specific boundary labels such as `submit_ready` or `confirm_current`

#### Scenario: Desktop-specific boundary steps remain internal adapter events
- **WHEN** the PingAn desktop implementation crosses broker-specific boundaries such as confirmation lookup or result dialog capture
- **THEN** the system MUST record those details as adapter-level event metadata
- **AND** the canonical public order status MUST remain expressed through the normalized order state model

### Requirement: Securities trader gateway SHALL persist canonical order and trade artifacts
The system SHALL persist canonical runtime artifacts for tracked orders, lifecycle events, and observed trades under a dedicated trader storage area.

#### Scenario: Canonical order execution writes trader artifacts
- **WHEN** a first-phase order executes through the canonical gateway
- **THEN** the system MUST append a canonical order-event record
- **AND** the system MUST persist a canonical order snapshot for the tracked order

#### Scenario: Observed fills are persisted separately from order snapshots
- **WHEN** the canonical gateway observes one or more trade fills for a tracked order
- **THEN** the system MUST write canonical trade-fill records
- **AND** those fill records MUST remain queryable independently from the order snapshot stream

### Requirement: Securities trader gateway SHALL expose local tracked-order query and same-day trade recovery
The system SHALL provide first-phase query and synchronization behavior for orders and trades that were created and tracked by the canonical gateway.

#### Scenario: Caller queries a locally tracked order
- **WHEN** a caller requests `query_order` for an order that was previously created through the canonical gateway
- **THEN** the system MUST return the latest canonical order snapshot reconstructed from the canonical trader store

#### Scenario: Caller queries locally tracked trades
- **WHEN** a caller requests `query_trades` for the first-phase canonical trader gateway
- **THEN** the system MUST return the observed trade fills currently persisted in the canonical trader store
- **AND** the behavior MUST be defined without requiring a full broker-side成交页抓取 implementation

#### Scenario: Caller requests same-day trade recovery
- **WHEN** a caller executes `sync_today_trades` through the first-phase canonical gateway
- **THEN** the system MUST rebuild the same-day tracked trade view from canonical persisted trader artifacts
- **AND** the synchronization contract MUST be limited to locally tracked orders and trades during the first phase

### Requirement: Securities trader gateway SHALL advertise gateway capability boundaries
The system SHALL expose normalized capability flags so callers can distinguish first-phase supported and unsupported securities trading behaviors.

#### Scenario: Caller inspects first-phase gateway capabilities
- **WHEN** a caller inspects the canonical gateway capabilities for the first-phase PingAn desktop implementation
- **THEN** the returned capability summary MUST distinguish supported behaviors such as buy/sell limit placement and tracked-order query
- **AND** the summary MUST also distinguish unsupported first-phase behaviors such as account query, position query, and broker-native push events
