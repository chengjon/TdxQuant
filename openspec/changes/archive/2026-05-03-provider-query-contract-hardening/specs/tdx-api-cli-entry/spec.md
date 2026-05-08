## ADDED Requirements

### Requirement: Query API CLI SHALL emit hardened query metadata for existing query entrypoints
The system SHALL preserve the stabilized query metadata contract on existing nested `api` and flat CLI query entrypoints for `market`, `meta`, `financial`, and `transaction`.

#### Scenario: Nested api query returns hardened query metadata
- **WHEN** a caller invokes a covered nested `api` query command
- **THEN** the CLI JSON result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: Flat query command returns hardened query metadata
- **WHEN** a caller invokes a covered flat query command
- **THEN** the CLI JSON result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: CLI preserves non-breaking query hardening contract
- **WHEN** a caller upgrades from the pre-hardening query contract to the hardened one
- **THEN** the CLI MUST preserve the existing top-level provider envelope
- **AND** new query metadata MUST be additive under `data.query_meta`

### Requirement: Query API CLI SHALL preserve replay-mode contract parity for covered query commands
The system SHALL keep replay-mode CLI query output contract-equivalent to live CLI query output for the covered query entrypoints.

#### Scenario: Replay-mode nested api query preserves query metadata contract
- **WHEN** a caller invokes a covered nested `api` query command with `--provider-mode replay`
- **THEN** the CLI MUST return the same hardened `data.query_meta` shape as the live query contract for that capability

#### Scenario: Replay-mode flat query preserves query metadata contract
- **WHEN** a caller invokes a covered flat query command with `--provider-mode replay`
- **THEN** the CLI MUST return the same hardened `data.query_meta` shape as the live query contract for that capability
