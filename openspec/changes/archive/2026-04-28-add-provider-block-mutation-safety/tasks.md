## 1. Contract Definition

- [x] 1.1 Define the provider-facing block mutation safety contract and manager/CLI deltas for custom-sector write actions.
- [x] 1.2 Decide the stable mutation summary fields, audit artifact exposure, and optional `mutation_key` behavior in docs/specs.

## 2. Implementation

- [x] 2.1 Add a shared block mutation helper that writes durable audit JSON files and normalizes mutation summaries.
- [x] 2.2 Extend block bridge, domain, manager, and CLI write entrypoints to accept mutation safety options and emit the shared contract.

## 3. Verification and Docs

- [x] 3.1 Add focused tests for bridge normalization, manager metadata/artifacts, and CLI parser/dispatch of mutation safety options.
- [x] 3.2 Document the provider block mutation safety contract and update roadmap/function-map references.
- [x] 3.3 Run focused tests, `python -m compileall tdxquant`, and `openspec validate add-provider-block-mutation-safety --type change --strict`.
