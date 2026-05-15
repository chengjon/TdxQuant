## Context

The desktop trading layer already has a broker/gateway abstraction (`GatewayCapabilities`, `TradeService`, `PingAnDesktopTraderGateway`) and stable PingAn desktop workflows for health, preflight, submit-ready, submit-once, buy/sell, and confirm-current. Extended broker capabilities are different: funds and positions are read-only account data surfaces, cancel order mutates broker state, and broker-native push would require a broker-side event source that is not present in the current desktop adapter.

The current PingAn desktop adapter already marks `supports_account_query`, `supports_position_query`, `supports_cancel`, and `supports_push_events` as false, but that evidence is not exposed as a stable diagnostic contract. The new package should make the boundary explicit without adding live account reads or side-effecting cancel behavior.

## Goals / Non-Goals

**Goals:**

- Provide a stable, machine-readable extended broker capability probe for PingAn desktop trading.
- Keep funds and positions as read-only probe entries and avoid collecting live account values.
- Classify cancel order as broker-state mutating even while unsupported.
- Record broker-native push as a feasibility boundary, not an available event stream.
- Expose the probe through the dedicated `trade` CLI namespace.
- Add independent risk documentation that explains read-only, local-state-mutating, and broker-state-mutating boundaries.

**Non-Goals:**

- Do not add funds/positions to the query-oriented `api` command group.
- Do not execute cancel order, account query, position query, or broker-native push subscription.
- Do not change `trade run`, buy/sell, submit-ready, confirm-current, task presets, or default upper-layer trading flows.
- Do not claim multi-broker production trading support.

## Decisions

1. Add a dedicated probe payload rather than expanding order placement contracts.
   - Rationale: funds, positions, cancel, and native push have different risk classes from order placement and should not appear as normal trading actions.
   - Alternative considered: add placeholder methods to `TradeService`. Rejected for this package because it would suggest executable capabilities that are intentionally out of scope.

2. Use existing `GatewayCapabilities` flags as evidence.
   - Rationale: the adapter already records whether PingAn desktop supports account query, position query, cancel, and push events. The probe can project those flags into a richer status/boundary schema.
   - Alternative considered: scrape the desktop client to discover screens. Rejected because the acceptance target is a read-only probe and side-effect boundary, not live account extraction.

3. Add `trade broker-capabilities` as a non-executing CLI entry.
   - Rationale: the existing `trade` namespace is the stable desktop trading surface and avoids merging broker capability diagnostics into `api`.
   - Alternative considered: add a flat legacy command. Rejected because new stable trading surfaces should prefer the nested `trade` group.

4. Keep broker-native push as a documented feasibility boundary.
   - Rationale: current subscription/SSE work projects provider artifacts and runtime state, not broker-native desktop events. The probe must not imply a live broker push stream exists.
   - Alternative considered: reuse provider subscription events. Rejected because that would mix market/provider push semantics with broker/trade lifecycle events.

## Risks / Trade-offs

- Readers may confuse "probe" with live account data access -> The payload MUST include `status`, `side_effect`, evidence, and boundaries for every capability.
- Unsupported cancel may be under-classified because no cancel is executed -> The cancel entry MUST classify the capability as broker-state mutating even when unavailable.
- Broker-native push can be confused with existing provider event streams -> The push entry MUST state that no broker-native event source is integrated.
- The CLI command can become another business contract if over-specified -> The command returns diagnostic metadata only and does not define business trading workflows.

## Migration Plan

No migration is required. This package adds a diagnostic command and docs without changing existing trade commands or runtime artifacts.

## Open Questions

- Which concrete PingAn desktop screens or broker APIs should become the first real account/position extraction target remains out of scope for this package.
- Whether cancel order should ever be automated through desktop UI requires a separate risk review and explicit user approval.
