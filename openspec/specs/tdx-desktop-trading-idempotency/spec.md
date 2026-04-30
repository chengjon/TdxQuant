# tdx-desktop-trading-idempotency Specification

## Purpose

定义稳定桌面交易工作流的 submission-key 幂等账本语义，包括 durable ledger、重复请求短路和冲突请求拒绝。
## Requirements
### Requirement: Stable desktop trade workflows SHALL persist a durable submission ledger for keyed requests
The system SHALL persist a durable local submission ledger row for every stable desktop trade request that includes a `submission_key`.

#### Scenario: Keyed request writes submission ledger row
- **WHEN** a caller executes a stable desktop trade workflow with a `submission_key`
- **THEN** the system MUST append a durable local ledger row that records the key, normalized request fingerprint, risk-gate outcome, and final result summary

### Requirement: Stable desktop trade workflows SHALL short-circuit duplicate keyed requests after side-effecting attempts
The system SHALL avoid repeating desktop side effects when a keyed stable trade request matches a prior side-effecting attempt for the same key and same normalized request fingerprint.

#### Scenario: Duplicate keyed request returns prior outcome without desktop execution
- **WHEN** a caller reuses a `submission_key` for the same normalized stable desktop trade request
- **AND** a prior ledger row for that key already passed the pre-trade risk gate
- **THEN** the workflow MUST return a duplicate-short-circuited result
- **AND** the desktop execution routine MUST NOT be called again

### Requirement: Stable desktop trade workflows SHALL reject conflicting keyed requests after side-effecting attempts
The system SHALL reject reuse of a `submission_key` for a different normalized trade request after a prior side-effecting attempt has already been recorded.

#### Scenario: Conflicting keyed request is rejected
- **WHEN** a caller reuses a `submission_key` for a different normalized stable desktop trade request
- **AND** a prior ledger row for that key already passed the pre-trade risk gate
- **THEN** the workflow MUST return an invalid-request style conflict result
- **AND** the desktop execution routine MUST NOT be called
