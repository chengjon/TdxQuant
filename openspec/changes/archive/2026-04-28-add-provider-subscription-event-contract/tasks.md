## 1. Contract Definition

- [x] 1.1 Define the provider-level subscription event row contract independently from the task transport.
- [x] 1.2 Update the `subscription-watch` spec to require conformance to the shared provider event contract.

## 2. Implementation

- [x] 2.1 Extract shared subscription event normalization helpers into a dedicated module.
- [x] 2.2 Refactor `subscription-watch` to emit rows through the shared helper without changing the current artifact contract.

## 3. Verification and Docs

- [x] 3.1 Add focused tests for shared event-row normalization and task integration output.
- [x] 3.2 Document the provider subscription event contract and update roadmap/function-map references.
- [x] 3.3 Run focused tests, `python -m compileall tdxquant`, and `openspec validate add-provider-subscription-event-contract --type change --strict`.
