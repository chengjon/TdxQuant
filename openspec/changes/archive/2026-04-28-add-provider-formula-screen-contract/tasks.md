## 1. Contract Definition

- [x] 1.1 Define the stable `formula.screen` payload shape, including normalized row schema and top-level summary fields.
- [x] 1.2 Define match normalization rules for raw TongDaXin stock-picking outputs and document the preferred entrypoint versus legacy raw entrypoints.

## 2. Implementation

- [x] 2.1 Add a shared formula screen normalization helper and a bridge wrapper that builds the stable contract from `formula_process_mul_xg`.
- [x] 2.2 Expose `screen(...)` through `FormulaApi` and `TdxApiManager.formula` while preserving `process_mul_xg(...)`.
- [x] 2.3 Add nested `api formula-screen` and flat `tdx-formula-screen` commands with canonical provider capability naming.

## 3. Verification and Docs

- [x] 3.1 Add bridge, manager, and CLI tests that lock the normalized stock-screen payload and provider result envelope behavior.
- [x] 3.2 Document the `formula.screen` contract and update roadmap/integration references to recommend it as the preferred stable formula entrypoint.
- [x] 3.3 Run focused tests, `python -m compileall tdxquant`, and `openspec validate add-provider-formula-screen-contract --type change --strict`.
