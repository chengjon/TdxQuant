## 1. Contract Definition

- [x] 1.1 Define the provider replay fixture bundle contract, including manifest fields and supported file formats.
- [x] 1.2 Fix the initial bundled fixture scope for the current high-value provider contracts.

## 2. Implementation

- [x] 2.1 Add packaged provider replay fixture assets under a stable package path.
- [x] 2.2 Add shared loader helpers for fixture catalog enumeration and JSON/JSONL loading.

## 3. Verification and Docs

- [x] 3.1 Add focused tests for fixture registry, loader behavior, and representative contract sample shapes.
- [x] 3.2 Document the provider replay fixture bundle and update roadmap/function-map references.
- [x] 3.3 Run focused tests, `python -m compileall tdxquant`, and `openspec validate add-provider-replay-fixtures --type change --strict`.
