## 1. Trader Domain Foundation

- [x] 1.1 Create the new `tdxquant/trader/` package with canonical enums, models, capability flags, and broker registry scaffolding for ordinary A-share cash limit `buy/sell`.
- [x] 1.2 Implement canonical trader storage for order events, order snapshots, and trade fills under `runtime/trader/`, including serialization rules for canonical price and timestamp fields.
- [x] 1.3 Implement the first-phase `TradeService` and `SecuritiesTraderGateway` interfaces for `connect`, `heartbeat`, `place_order`, `query_order`, `query_trades`, and `sync_today_trades`.

## 2. PingAn Desktop Gateway

- [x] 2.1 Implement `PingAnDesktopTraderGateway` by adapting the existing desktop buy flow into a canonical `side=buy` order-placement path and recording desktop boundary steps as adapter metadata.
- [x] 2.2 Add the first-phase `side=sell` PingAn desktop workflow, including sell-page activation, sell-submit execution, and canonical order-state mapping.
- [x] 2.3 Wire canonical tracked-order query and same-day trade recovery for PingAn desktop orders using canonical trader storage without requiring full broker-side query-page scraping.

## 3. CLI And Compatibility Migration

- [x] 3.1 Add broker-neutral CLI commands for `trade order-place`, `trade order-query`, and `trade trade-query`, with first-phase ordinary A-share limit-order argument validation.
- [x] 3.2 Preserve `trade buy` and `trade submit-once` as compatibility commands by forwarding them into the canonical trader service where the caller contract remains equivalent.
- [x] 3.3 Keep `trade submit-ready` and `trade confirm-current` available as explicit PingAn desktop boundary commands without promoting them into canonical order states.

## 4. Verification And Documentation

- [x] 4.1 Add or update tests for canonical trader models, storage, PingAn desktop gateway behavior, new CLI commands, and compatibility command forwarding.
- [x] 4.2 Update architecture and operator-facing documentation to describe the new securities trader mainline, first-phase scope, and migration boundaries between canonical trader storage and legacy `pingan-*` artifacts.
- [x] 4.3 Run targeted verification for the new trader path and finish with `openspec validate add-securities-trader-gateway --type change --strict`.
