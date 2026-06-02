## ADDED Requirements

### Requirement: Desktop trading management SHALL group PingAn confirm-current seam callbacks behind an internal handler bundle
The desktop trading management layer SHALL allow the PingAn confirm-current execution seam to receive rejection, metadata, safety metadata, and finalization callbacks through an internal handler bundle.

#### Scenario: Confirm-current seam handler bundle remains internal

- **WHEN** `confirm_current` routes a normalized request through `execute_pingan_confirm_current`
- **THEN** the manager SHOULD pass confirm-current result policy through an internal `PingAnConfirmCurrentExecutionHandlers` bundle
- **AND** the seam MUST preserve existing gate rejection, dispatch timing, metadata, safety metadata, finalize, and result payload behavior
- **AND** direct internal callers MAY continue to pass the existing individual callback arguments for compatibility
- **AND** desktop confirm lookup, click, result-dialog lookup, and result-dialog close dispatch SHOULD remain in the manager callsite
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, desktop primitive, live readiness, or production trading behavior
