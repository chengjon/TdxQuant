## 1. Bundle contract formalization

- [x] 1.1 Add a stable `read-zxg-review` bundle requirement to the command-catalog spec.
- [x] 1.2 Document that the bundle continues to reuse the existing `command-bundles.json` schema and preset-backed entry dispatch path.
- [x] 1.3 Document that bundle-level `--block-code` fans out to both `read-zxg-watchlist` and `read-zxg-full`.

## 2. Lifecycle sync

- [x] 2.1 Verify the existing implementation and focused tests cover default bundle listing visibility, bundle inspection, plan, and run for `read-zxg-review`.
- [x] 2.2 Verify the focused tests cover bundle-level `--block-code` fanout and step-1-failure short-circuit.
- [x] 2.3 Sync the approved bundle contract into the main OpenSpec spec set and fix stale docs that still claimed pure-read review bundling was deferred.

## 3. Validation and archive

- [x] 3.1 Run `openspec validate catalog-block-read-watchlist-review-bundle --type change --strict`.
- [x] 3.2 Archive the completed change after spec sync.
