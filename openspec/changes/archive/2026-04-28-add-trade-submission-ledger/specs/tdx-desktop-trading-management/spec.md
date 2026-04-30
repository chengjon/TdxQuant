## ADDED Requirements

### Requirement: Desktop trading management SHALL expose submission-ledger artifacts for keyed stable workflows
The system SHALL expose the durable submission-ledger artifact path for keyed stable desktop trade workflows.

#### Scenario: Keyed trade result exposes ledger artifact path
- **WHEN** a keyed stable desktop trade workflow finishes through `TdxTradeManager`
- **THEN** the result artifacts MUST expose the durable submission-ledger path

### Requirement: Desktop trading management SHALL consult the submission ledger before stable desktop execution
The system SHALL consult the durable submission ledger before executing a keyed stable desktop trade workflow.

#### Scenario: Submission ledger prevents duplicate desktop execution
- **WHEN** a keyed stable desktop trade workflow is invoked
- **THEN** the management layer MUST consult the current submission ledger before desktop execution
- **AND** the management layer MUST apply duplicate-short-circuit or conflicting-key rejection behavior when the ledger requires it
