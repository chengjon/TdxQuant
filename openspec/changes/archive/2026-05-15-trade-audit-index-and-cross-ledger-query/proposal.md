## Why

Existing trade audit lookup and daily/period reports scan audit files directly and do not provide a stable way to correlate trade audit records with submission-key history or task ledger rows. The next P1 gap is to add a read-only index/query layer that makes repeated diagnostics faster and gives operators one place to inspect cross-ledger evidence without rewriting historical artifacts.

## What Changes

- Add a trade audit index cache schema that records normalized audit entries, source file metadata, scan counts, and load warnings.
- Add a read-only cross-ledger query entrypoint that joins trade audit entries with PingAn submission ledger rows and task ledger rows by stable keys such as `submission_key`, `contract_no`, and `code`.
- Add corrupt-file tolerance so malformed audit or ledger files produce warnings and partial results instead of aborting the whole query.
- Add focused tests for cache shape, join rules, filters, and damaged input handling.

## Capabilities

### New Capabilities

- `tdx-trade-audit-index-cross-ledger-query`: Covers the normalized audit index cache and read-only cross-ledger query contract for trade audit, submission ledger, and task ledger diagnostics.

### Modified Capabilities

- `tdx-task-management`: Adds a stable manager-backed task entrypoint for the read-only trade audit cross-ledger query.

## Impact

- Affected code: `tdxquant/api/task.py`, `tdxquant/cli.py`, `tdxquant/tasking.py`, `tdxquant/reporting.py`, focused tests, runtime command/catalog presets if the task entrypoint is exposed there.
- Affected specs: new trade audit index/query spec plus task management delta.
- No dependency changes.
- No writes to historical trade audit, submission ledger, or task ledger artifacts.
