## ADDED Requirements

### Requirement: Query API management SHALL expose block write mutation safety metadata
The system SHALL make block-domain write actions return standardized mutation summaries and audit artifact metadata through `TdxApiManager.block`.

#### Scenario: Manager block write returns mutation summary and artifact
- **WHEN** a caller invokes `manager.block.create_sector(...)`, `delete_sector(...)`, `rename_sector(...)`, `clear_sector(...)`, or `send_user_block(...)`
- **THEN** the returned provider-facing result MUST include a stable `data.block_mutation` summary
- **AND** the result MUST expose the audit artifact through provider artifacts and local artifact metadata

### Requirement: Query API management SHALL accept explicit block mutation safety options
The system SHALL allow callers to pass mutation safety options explicitly through block-domain write methods instead of inferring them from API profiles.

#### Scenario: Caller passes mutation safety options through manager block write
- **WHEN** a caller invokes a manager block write action with `mutation_key` and/or `audit_dir`
- **THEN** the manager MUST forward those options unchanged to the block-domain implementation and preserve them in the returned mutation contract
