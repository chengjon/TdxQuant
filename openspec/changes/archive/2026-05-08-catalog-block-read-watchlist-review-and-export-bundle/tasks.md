## 1. Bundle contract formalization

- [x] 1.1 Add a stable `read-zxg-review-and-export` bundle requirement to the command-catalog spec.
- [x] 1.2 Document that the bundle continues to reuse the existing `command-bundles.json` schema and preset-backed entry dispatch path.
- [x] 1.3 Document the fixed three-step order: `read-zxg-watchlist`, `read-zxg-full`, `export-zxg-watchlist`.
- [x] 1.4 Document that bundle-level `--block-code` fans out to all three steps.
- [x] 1.5 Document that `export_output` and `overwrite` remain preset-owned and are not bundle-level overrides.

## 2. Implementation and coverage

- [x] 2.1 Add the `read-zxg-review-and-export` bundle definition.
- [x] 2.2 Verify focused tests cover default bundle listing visibility, bundle inspection, plan, and run.
- [x] 2.3 Verify focused tests cover bundle-level `--block-code` fanout across all three steps.
- [x] 2.4 Verify focused tests cover stop-before-export when `read-zxg-full` fails.
- [x] 2.5 Verify focused tests cover export-step failure propagation.
- [x] 2.6 Verify focused tests cover unsupported bundle-level export overrides.

## 3. Lifecycle sync

- [x] 3.1 Sync the approved bundle contract into the main OpenSpec spec set.
- [x] 3.2 Sync user-facing task/catalog docs and the project function map.
- [x] 3.3 Preserve documentation for the existing pure-read `read-zxg-review` bundle.

## 4. Validation and archive

- [x] 4.1 Run focused catalog CLI tests for `read-zxg-review-and-export`.
- [x] 4.2 Run full `tests/test_api_cli.py`.
- [x] 4.3 Run bundle resolver tests.
- [x] 4.4 Run `openspec validate catalog-block-read-watchlist-review-and-export-bundle --type change --strict`.
- [x] 4.5 Archive the completed change after spec sync.
