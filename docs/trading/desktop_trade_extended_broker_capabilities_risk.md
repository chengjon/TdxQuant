# Desktop Trade Extended Broker Capabilities Risk Boundary

This document defines the risk boundary for PingAn desktop extended broker capabilities exposed by `trade broker-capabilities`.

## Scope

The current capability probe is diagnostic metadata. It reports whether the PingAn desktop gateway advertises funds, positions, cancel order, or broker-native push support. It does not execute any account query, holding query, cancel request, or push subscription.

## Risk Classes

### read-only

Funds and positions are registered as read-only probe entries. In this package, read-only means the probe can report capability status and boundary metadata, but it must not extract balances, available cash, account identifiers, holdings, costs, market values, or broker screen contents.

### local-state-mutating

Local-state-mutating actions can write local diagnostic artifacts, ledgers, audit files, or cache files without changing broker state. The extended broker capability probe itself should normally avoid local writes other than optional CLI output selected by the caller.

### broker-state-mutating

Cancel order is broker-state-mutating because a real cancel request can alter an order at the broker. The probe only classifies this risk and must not submit a cancel request. Any future cancel workflow requires a separate OpenSpec change, explicit side-effect gate, audit semantics, idempotency strategy, and focused tests.

## Broker-Native Push Boundary

Broker-native push means an event source emitted by the broker or desktop trading runtime for account/order/trade lifecycle updates. Existing provider subscription streams, bridge SSE projections, and market-data watch events do not satisfy this boundary. Until a broker-native event source is integrated and tested, push support remains unsupported.

## Non-Scope

- No live funds query.
- No live positions query.
- No cancel order execution.
- No broker-native push subscription.
- No merge into the query-oriented `api` namespace.
- No promotion to the default upper-layer trading mainline.
