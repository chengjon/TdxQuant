## ADDED Requirements

### Requirement: Trade CLI SHALL expose a summary view for PingAn acceptance evidence

The stable trade CLI SHALL expose a compact summary view for PingAn trade execution acceptance evidence without changing the detailed default output.

#### Scenario: CLI parses acceptance evidence summary view

- **WHEN** an operator runs `trade acceptance-evidence --view summary`
- **THEN** the CLI MUST parse the command as a read-only PingAn acceptance evidence request
- **AND** it MUST preserve `detailed` as the default view when no view is provided.

#### Scenario: Summary view exposes stable read-only acceptance fields

- **WHEN** `trade acceptance-evidence --view summary` is handled
- **THEN** the result MUST include `summary_view` with target nodes, covered commands/methods, evidence category names, artifact target keys, and side-effect flags
- **AND** the summary MUST report no trade dispatch, order submission, workflow dispatch, desktop automation, process control, catalog dispatch, live/manual acceptance evaluation, or status transition execution.
