## ADDED Requirements

### Requirement: Provider block sync SHALL expose a dedicated watchlist-to-block synchronization capability
The system SHALL expose a dedicated provider-facing block synchronization capability for pushing a normalized watchlist into a TongDaXin custom sector without forcing callers to compose lower-level write actions manually.

#### Scenario: Caller invokes block sync through a provider-facing contract
- **WHEN** a caller requests watchlist-to-block synchronization
- **THEN** the system MUST expose a dedicated block sync capability rather than requiring the caller to infer synchronization semantics from raw `send_user_block` behavior

### Requirement: Provider block sync SHALL support replace and merge synchronization modes
The system SHALL support both `replace` and `merge` synchronization modes and SHALL treat `replace` as the default mode when the caller does not specify one explicitly.

#### Scenario: Caller omits sync mode
- **WHEN** a caller requests block synchronization without an explicit mode
- **THEN** the system MUST treat the request as `replace`

#### Scenario: Replace mode computes a full target set
- **WHEN** a caller invokes block sync with `mode=replace`
- **THEN** the desired member set MUST equal the normalized requested symbol set
- **AND** the result MUST allow non-empty `removed_symbols`

#### Scenario: Merge mode only appends missing symbols
- **WHEN** a caller invokes block sync with `mode=merge`
- **THEN** the desired member set MUST equal the observed member set union the normalized requested symbol set
- **AND** the result MUST report an empty `removed_symbols` set

#### Scenario: Merge mode becomes noop when every requested symbol is already present
- **WHEN** a caller invokes block sync with `mode=merge` and every normalized requested symbol already exists in the observed member set
- **THEN** the system MUST return a stable noop-style sync outcome instead of executing a new runtime write

### Requirement: Provider block sync SHALL support explicit create-if-missing behavior
The system SHALL support an explicit `create_if_missing` flag so callers can choose whether a missing target block should be rejected or created before synchronization continues.

#### Scenario: Missing target block is rejected by default
- **WHEN** a caller requests block sync for a nonexistent block without `create_if_missing=true`
- **THEN** the system MUST reject the request before executing an underlying runtime write

#### Scenario: Missing target block is planned but not created during dry run
- **WHEN** a caller requests block sync for a nonexistent block with `create_if_missing=true` and `dry_run=true`
- **THEN** the system MUST report a plan that includes block creation semantics
- **AND** the system MUST NOT execute a real create-sector write
- **AND** the sync summary MUST report `created_block=false`

#### Scenario: Missing target block is created during live sync
- **WHEN** a caller requests block sync for a nonexistent block with `create_if_missing=true` and `dry_run=false`
- **THEN** the system MUST create the target block before attempting the member synchronization write

### Requirement: Provider block sync SHALL support dry-run planning without real writes
The system SHALL support `dry_run=true` and SHALL still compute normalized desired state, diffs, and governance decisions while preventing any real runtime mutation.

#### Scenario: Dry run returns a full synchronization plan
- **WHEN** a caller requests block sync with `dry_run=true`
- **THEN** the response MUST include normalized observed symbols, desired symbols, added symbols, removed symbols, unchanged symbols, and governance fields
- **AND** the system MUST NOT execute create-sector or send-user-block runtime writes

#### Scenario: Dry run still writes a durable audit artifact
- **WHEN** a caller requests block sync with `dry_run=true`
- **THEN** the system MUST still expose a durable audit artifact descriptor for the sync outcome

### Requirement: Provider block sync SHALL support an explicit show execution option
The system SHALL support an explicit `show` execution option for block synchronization, SHALL default that option to `true`, and SHALL treat it as an execution-time option rather than as part of the desired membership set comparison.

#### Scenario: Caller omits show option
- **WHEN** a caller invokes block sync without an explicit `show` option
- **THEN** the system MUST default `show` to `true`

#### Scenario: Show option does not affect desired member diff
- **WHEN** a caller invokes block sync with the same normalized symbol set but a different `show` value
- **THEN** the desired member set comparison MUST remain unchanged

### Requirement: Provider block sync SHALL return a stable sync-focused summary
The system SHALL expose a stable sync-focused summary so callers can reason about what changed without parsing lower-level mutation details.

#### Scenario: Live or dry-run block sync returns a normalized summary
- **WHEN** a caller invokes block sync
- **THEN** the response `data` MUST include a `sync` object containing `block_code`, `mode`, `create_if_missing`, `dry_run`, `show`, `status`, `governance_decision`, `governance_reason`, `created_block`, `would_create_block`, `added_symbols`, `removed_symbols`, `unchanged_symbols`, `desired_symbols`, and `observed_symbols`

### Requirement: Provider block sync SHALL preserve underlying block mutation metadata for executed writes
The system SHALL preserve lower-level `block_mutation` metadata and audit artifact descriptors for synchronization requests that execute or plan governed block writes.

#### Scenario: Block sync reuses block mutation governance
- **WHEN** a block sync request reaches a governed create-sector or send-user-block stage
- **THEN** the response MUST preserve lower-level `block_mutation` metadata alongside the higher-level `sync` summary
- **AND** the response MUST expose audit artifact descriptors for the governed write path

#### Scenario: Sync mutation key does not redefine underlying write mutation identity
- **WHEN** a caller provides a sync-level `mutation_key`
- **THEN** the sync capability MUST use that key for sync-level replay and conflict decisions
- **AND** the system MUST NOT require the same key to become the mutation identity for each underlying governed write stage

### Requirement: Provider block sync SHALL enforce sync-level mutation key replay and conflict rules
The system SHALL preserve an optional caller-supplied `mutation_key` across the block sync contract while evaluating replay and conflict behavior against the canonical block sync request.

#### Scenario: Caller replays the same sync request with the same mutation key
- **WHEN** a caller repeats the same canonical block sync request with the same `mutation_key`
- **THEN** the system MUST short-circuit the duplicate request without executing a new runtime write

#### Scenario: Caller reuses a mutation key for a different sync request
- **WHEN** a caller reuses a prior `mutation_key` for a different canonical block sync request
- **THEN** the system MUST reject the request before executing a runtime write

### Requirement: Provider block sync SHALL reject malformed or incomplete sync requests with stable failures
The system SHALL reject malformed sync requests and SHALL stabilize failures that occur before or during governed write execution.

#### Scenario: Caller provides an empty symbol list
- **WHEN** a caller invokes block sync without any normalized symbols
- **THEN** the system MUST reject the request with a stable invalid-request style failure before any runtime write occurs

#### Scenario: Observed-state probe fails before sync decision
- **WHEN** the system cannot read the target block state required for a block sync decision
- **THEN** the system MUST return a stable failure result and MUST NOT execute a runtime write

#### Scenario: Create succeeds but member update fails
- **WHEN** a live block sync creates a missing block and the subsequent governed member update fails
- **THEN** the system MUST return a stable failure result that preserves the partial execution metadata and audit artifacts for the underlying write stages
