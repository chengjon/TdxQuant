## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register D-13 summary view evidence

`FUNCTION_TREE.md` SHALL register the PingAn acceptance evidence summary view as D-13 evidence.

#### Scenario: D-13 cites summary view evidence

- **WHEN** `trade acceptance-evidence --view summary` is implemented
- **THEN** D-13 MUST cite the CLI summary view, tests, and this OpenSpec change as evidence
- **AND** the boundary MUST state that the summary view is read-only and does not execute trades, broker probes, desktop automation, task/report/bundle/catalog dispatch, live/manual acceptance evaluation, or status transitions.
