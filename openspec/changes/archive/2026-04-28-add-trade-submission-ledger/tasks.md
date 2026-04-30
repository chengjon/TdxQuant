## 1. OpenSpec And Tests

- [x] 1.1 Add RED tests for duplicate keyed trade short-circuit, conflicting-key rejection, and submission-ledger persistence.
- [x] 1.2 Update CLI-facing tests for the new submission-ledger artifact wiring where needed.

## 2. Ledger Implementation

- [x] 2.1 Add submission-ledger path, fingerprint, load, and append helpers under `tdxquant/trade/`.
- [x] 2.2 Extend `TdxTradeManager` stable workflows to consult the ledger before desktop execution and append ledger rows after finalization.
- [x] 2.3 Surface normalized idempotency summary and ledger artifact paths in stable trade results.

## 3. Documentation And Verification

- [x] 3.1 Update docs to reflect that `submission_key` is now a real idempotent control for stable desktop trade workflows.
- [x] 3.2 Run focused pytest, compile, and OpenSpec validation, then archive the change if complete.
