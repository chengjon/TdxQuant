## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn trade acceptance evidence summary without over-claiming

`FUNCTION_TREE.md` SHALL register the read-only PingAn trade execution acceptance evidence summary as a D-07/D-08-linked feature node while preserving explicit boundaries.

#### Scenario: Registry cites acceptance evidence summary as a bounded D-07/D-08-linked node

- **WHEN** `trade acceptance-evidence` and `TdxTradeManager.pingan.acceptance_evidence` exist
- **THEN** `FUNCTION_TREE.md` MUST cite the code, tests, and this OpenSpec change in the PingAn trade execution acceptance evidence summary node
- **AND** the boundary MUST state that the summary is read-only and does not execute trades, prove broker production readiness, complete live/manual acceptance, or automatically transition status.
