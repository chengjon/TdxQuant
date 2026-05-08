## 1. Governance Core

- [x] 1.1 Refactor `tdxquant/block_mutation.py` from a post-write wrapper into a governance entrypoint that can normalize requests, compare observed state, and decide `execute / skip / reject`.
- [x] 1.2 Add local `mutation_key` idempotency and conflict handling for all supported block write operations.
- [x] 1.3 Extend the stable `block_mutation` summary and audit artifact payload with governance-specific fields and status values.

## 2. Block Write Integration

- [x] 2.1 Update the five block write bridges to pass the required read-state inputs and underlying write callback into the governance layer.
- [x] 2.2 Implement operation-specific desired-state comparison rules for `create_sector`, `delete_sector`, `rename_sector`, `clear_sector`, and `send_user_block`.
- [x] 2.3 Keep existing manager and CLI entrypoints stable while preserving the new governance outcomes through the current result contract.

## 3. Fixtures, Tests, And Docs

- [x] 3.1 Add or update representative block governance fixtures for applied, noop, and rejected outcomes.
- [x] 3.2 Add targeted tests covering bridge governance decisions, manager passthrough, and CLI stability.
- [x] 3.3 Update block governance documentation and validate the change with strict OpenSpec checks plus targeted pytest coverage.
