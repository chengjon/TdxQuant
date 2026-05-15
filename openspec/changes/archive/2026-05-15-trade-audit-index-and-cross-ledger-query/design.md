## Context

Trade audit tasks already support lookup, daily report, and period report by scanning `runtime/trade-audits/*.json`. PingAn submission history is stored separately in `runtime/pingan-submission-ledger.jsonl`, while task trade reports use the guarded task ledger under `runtime/exports`. Operators currently need to manually combine those artifacts when diagnosing duplicate submission keys, trade outcomes, or task-level report lineage.

This change adds a derived, read-only index/query layer. The index cache is not a source of truth; it can always be rebuilt from audit files. Cross-ledger query results must preserve source paths and warnings so consumers can see which evidence was joined and which files were skipped.

## Goals / Non-Goals

**Goals:**

- Normalize trade audit files into a cache payload with schema version, source metadata, entries, and warnings.
- Join audit entries to submission ledger rows and task ledger rows using stable keys.
- Provide a manager-backed task entrypoint and CLI parser for the read-only query.
- Tolerate corrupt audit and JSONL files by returning partial results with warnings.

**Non-Goals:**

- Do not rewrite historical audit, submission ledger, or task ledger files.
- Do not compute trade amount, quantity, price, or PnL aggregation.
- Do not add a live broker/provider schema.
- Do not make the derived cache more authoritative than the original artifacts.

## Decisions

1. Use a small pure-Python helper module for index and join logic.
   - Rationale: the logic is reusable from `TdxTaskManager` and focused tests without further growing task dispatch code.
   - Alternative considered: keep everything private in `tdxquant/api/task.py`. That would be less discoverable and harder to test directly.

2. Treat cache files as optional derived artifacts.
   - Rationale: existing audit files remain the source of truth. Query callers can request a cache output path, but missing cache files do not block direct scans.
   - Alternative considered: maintain an always-on persistent cache. That would introduce invalidation and migration concerns outside this small package.

3. Join deterministically by exact keys only.
   - Rationale: `submission_key`, `contract_no`, and `code` are already present in existing artifacts. Fuzzy joins would risk false operational conclusions.
   - Alternative considered: infer joins by date/time proximity. That is too ambiguous for safety diagnostics.

4. Keep error handling warning-based for damaged individual files.
   - Rationale: a single malformed audit or JSONL line should not hide the rest of the evidence. Missing top-level sources still return structured empty results or `PATH_NOT_FOUND` where appropriate.

## Risks / Trade-offs

- Corrupt files can still reduce result completeness -> every skipped file or JSONL line is returned in `warnings`.
- Exact-key joins can miss evidence when older artifacts lack keys -> results include empty join arrays rather than inferred matches.
- Cache payloads may grow with audit volume -> this package stores compact normalized entries, not full historical audit payloads.
- Adding a task/CLI entry increases command surface -> it is read-only and uses existing `TdxTaskManager` metadata.
