# tdx-trade-audit-index-cross-ledger-query Specification

## Purpose
TBD - created by archiving change trade-audit-index-and-cross-ledger-query. Update Purpose after archive.
## Requirements
### Requirement: Trade audit index cache SHALL normalize audit files without mutating sources
The system SHALL build a derived trade audit index cache from a trade audit directory. The cache payload MUST include a schema version, source metadata, scan counts, normalized entries, and load warnings, and MUST NOT modify the source audit files.

#### Scenario: Cache includes normalized audit entries
- **WHEN** a caller builds an index from a directory containing valid trade audit JSON files
- **THEN** the cache payload includes `schema_version`, `source.audit_dir`, `summary.scanned_files`, `summary.indexed_entries`, and an `entries` list containing normalized `audit_id`, `recorded_at`, `status`, `broker`, `method`, `code`, `contract_no`, `submission_key`, and `audit_path` fields

#### Scenario: Corrupt audit files are skipped with warnings
- **WHEN** a caller builds an index from a directory containing both valid and malformed audit JSON files
- **THEN** valid files are still indexed
- **AND** malformed files are reported in `warnings`
- **AND** no source audit file is rewritten

### Requirement: Trade audit cross-ledger query SHALL join evidence read-only
The system SHALL provide a read-only query that correlates indexed trade audit entries with PingAn submission ledger rows and task ledger rows. The query MUST join by exact stable keys and MUST NOT rewrite trade audit files, submission ledgers, task ledgers, or cache inputs.

#### Scenario: Query joins audit entries to submission and task ledgers
- **WHEN** a trade audit entry has a `submission_key`, `contract_no`, and `code` matching rows in the submission ledger and task ledger
- **THEN** the returned row includes the normalized audit entry
- **AND** includes matching submission ledger rows under `submission_matches`
- **AND** includes matching task ledger rows under `task_matches`
- **AND** the response describes the exact join keys used

#### Scenario: Damaged ledger rows do not abort the query
- **WHEN** a submission ledger or task ledger contains malformed JSONL lines
- **THEN** valid rows are still available for joins
- **AND** malformed lines are reported in `warnings`

### Requirement: Trade audit cross-ledger query SHALL filter and order results
The system SHALL allow the read-only query to filter by audit fields and return deterministic newest-first results.

#### Scenario: Query filters by submission key and status
- **WHEN** a caller filters by `submission_key` and `status`
- **THEN** only audit entries matching both filters are returned
- **AND** results are ordered by `recorded_at` newest first

#### Scenario: Query respects result limits
- **WHEN** a caller supplies a positive `limit`
- **THEN** the query returns at most that many result rows while preserving summary counts for the full filtered set

