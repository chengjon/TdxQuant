## 1. Query metadata normalization

- [x] 1.1 Add hardened `data.query_meta` helpers and the stable `{domain}.{method}` `query_kind` registry for covered `market / meta / financial / transaction` capabilities in the bridge/provider-result boundary
- [x] 1.2 Apply the shared query metadata contract to existing manager query entrypoints without introducing new commands or API shapes, preserving effective `requested_fields` semantics and `query_params` passthrough
- [x] 1.3 Add focused tests for success, empty-result, and selector-field behavior across representative covered queries: `market.snapshot`, `market.kline`, `meta.stock_list`, `meta.sector_stocks`, `financial.financial_data`, `financial.financial_data_by_date`, `transaction.stock_transaction_data`, and `transaction.market_transaction_data`

## 2. CLI and replay alignment

- [x] 2.1 Ensure nested `api` and flat CLI query entrypoints emit the hardened query metadata contract
- [x] 2.2 Add representative replay fixtures and default replay mapping for covered query capabilities with minimum coverage for `market.snapshot`, `market.kline`, `meta.stock_list`, `meta.sector_stocks`, `financial.financial_data`, `financial.financial_data_by_date`, `transaction.stock_transaction_data`, and `transaction.market_transaction_data`, plus empty/failure representatives across the covered domains
- [x] 2.3 Add CLI and replay tests in the query contract / CLI / replay fixture suites that lock live/replay contract parity for covered queries, including `data.query_meta` shape and non-breaking additive output behavior

## 3. Discovery, docs, and verification

- [x] 3.1 Extend capability discovery metadata for covered query capabilities with a stable `query_metadata.query_shapes` object-list shape plus field-selection, empty-result, and replay hints
- [x] 3.2 Update provider query, replay fixture, and project roadmap docs to reflect the hardened query contract as additive / non-breaking hardening
- [x] 3.3 Run targeted manager/CLI/replay/discovery verification plus `openspec validate provider-query-contract-hardening --type change --strict`
