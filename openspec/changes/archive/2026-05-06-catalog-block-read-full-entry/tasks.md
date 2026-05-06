## 1. Catalog entry formalization

- [x] 1.1 Add a stable `read-zxg-full` entry requirement to the command-catalog spec.
- [x] 1.2 Document that the entry continues to reuse the existing command-catalog schema and preset-backed dispatch path.

## 2. Lifecycle sync

- [x] 2.1 Verify the existing implementation and focused tests cover default listing visibility, single-entry inspection, plan, and run for `read-zxg-full`.
- [x] 2.2 Sync the approved catalog-entry contract into the main OpenSpec spec set and fix stale docs that still claimed catalog packaging was deferred.

## 3. Validation and archive

- [x] 3.1 Run `openspec validate catalog-block-read-full-entry --type change --strict`.
- [x] 3.2 Archive the completed change after spec sync.
