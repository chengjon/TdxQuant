## MODIFIED Requirements

### Requirement: Provider block mutation safety SHALL expose a stable mutation summary
The system SHALL expose a stable capability-specific mutation summary for TongDaXin custom-sector write actions so callers can reason about attempted and skipped state changes without parsing free-form messages.

#### Scenario: Block write returns normalized mutation summary
- **WHEN** a caller invokes a provider-facing custom-sector write action
- **THEN** the response `data` MUST include a `block_mutation` object with stable identity, operation, target, status, governance decision, governance reason, desired state, and observed state fields
- **AND** `status` MUST use the stable values `applied`, `noop`, `rejected`, or `failed`

### Requirement: Provider block mutation safety SHALL write a durable local audit artifact for every write attempt
The system SHALL write a local JSON audit artifact for every supported custom-sector write attempt, including applied, skipped, rejected, and failed outcomes.

#### Scenario: Successful block mutation writes audit artifact
- **WHEN** a custom-sector write action executes and succeeds
- **THEN** the response MUST expose an audit artifact path and the written audit file MUST describe the attempted mutation, governance decision, and final result

#### Scenario: Governance skip also writes audit artifact
- **WHEN** a custom-sector write action is skipped because the current state already matches the requested target state
- **THEN** the response MUST still expose an audit artifact path
- **AND** the written audit file MUST record a `noop` status together with the governance reason and observed state

#### Scenario: Governance rejection also writes audit artifact
- **WHEN** a custom-sector write action is rejected before executing the underlying runtime write
- **THEN** the response MUST still expose an audit artifact path
- **AND** the written audit file MUST capture the rejection reason and the observed state that caused it

### Requirement: Provider block mutation safety SHALL preserve an optional caller mutation key
The system SHALL preserve an optional caller-supplied `mutation_key` across the result payload and audit artifact while also enforcing stable local idempotency and conflict detection.

#### Scenario: Caller provides mutation key for the first matching request
- **WHEN** a caller passes a `mutation_key` for a supported custom-sector write action and no conflicting prior request exists for that key
- **THEN** the response `data.block_mutation` and audit artifact MUST contain the same key
- **AND** the governance layer MUST continue evaluating the current block state before deciding whether to execute, skip, or reject

#### Scenario: Caller reuses mutation key with the same normalized request
- **WHEN** a caller replays the same supported custom-sector write action with the same `mutation_key` and the same normalized request content
- **THEN** the system MUST short-circuit the request without executing a new underlying runtime write
- **AND** the response MUST report a stable governance outcome for the duplicate replay

#### Scenario: Caller reuses mutation key with a different normalized request
- **WHEN** a caller reuses a prior `mutation_key` for a different normalized request
- **THEN** the system MUST reject the request before executing the underlying runtime write
- **AND** the response and audit artifact MUST report the mutation-key conflict explicitly
