# tdx-block-sync-write-policy Delta

## ADDED Requirements

### Requirement: High-level block sync entries SHALL honor explicit write policies

The system SHALL expose the existing block sync `write_policy` contract through high-level API, task, and CLI block sync entry points without changing provider-level mutation semantics.

#### Scenario: Caller plans a merge dry-run through task block sync

- **WHEN** a caller invokes `task block-sync` with `--write-policy merge_dry_run`
- **THEN** the task MUST pass `write_policy=merge_dry_run` to the block sync manager path
- **AND** the resulting sync summary MUST remain a dry-run plan rather than a provider write

#### Scenario: Caller supplies conflicting policy and legacy flags

- **WHEN** a caller invokes block sync with an explicit `write_policy` that conflicts with `mode` or `dry_run`
- **THEN** the existing block sync write-policy conflict behavior MUST reject the request rather than silently choosing one interpretation

