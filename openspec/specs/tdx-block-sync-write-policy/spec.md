# tdx-block-sync-write-policy Specification

## Purpose
TBD - created by archiving change block-sync-write-policy-hardening. Update Purpose after archive.
## Requirements
### Requirement: Block sync write policy SHALL define explicit write intent
The system SHALL expose a stable write policy enum for block sync operations.

#### Scenario: Replace policy maps to replace execution
- **WHEN** a caller requests write policy `replace`
- **THEN** the system MUST execute the existing replace sync behavior
- **AND** it MUST record write policy metadata in the sync result

#### Scenario: Merge dry-run policy maps to merge planning
- **WHEN** a caller requests write policy `merge_dry_run`
- **THEN** the system MUST use merge semantics with `dry_run=true`
- **AND** it MUST NOT invoke live block mutation writes

#### Scenario: Conflicting policy and mode are rejected
- **WHEN** a caller requests a write policy that conflicts with explicit mode or dry-run options
- **THEN** the system MUST return a stable invalid-request failure
- **AND** block mutation writes MUST NOT be invoked

### Requirement: Block sync write policy SHALL be audit-visible
The system SHALL include policy metadata in block sync result and audit artifacts.

#### Scenario: Audit artifact includes policy metadata
- **WHEN** a block sync operation writes an audit artifact
- **THEN** the artifact MUST include write policy, resolved mode, dry-run flag, and canonical request policy fields

