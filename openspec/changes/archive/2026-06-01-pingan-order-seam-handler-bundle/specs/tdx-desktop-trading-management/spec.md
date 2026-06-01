## ADDED Requirements

### Requirement: Desktop trading management SHALL group PingAn order seam callbacks behind an internal handler bundle
The desktop trading management layer SHALL support grouping internal PingAn order execution seam callbacks into a handler bundle while preserving existing order seam behavior and public manager contracts.

#### Scenario: Order seam handler bundle remains internal

- **WHEN** buy, sell, or submit-once manager paths call `execute_pingan_order`
- **THEN** they SHOULD pass a grouped internal handler bundle for duplicate, conflict, risk rejection, and finalize callbacks
- **AND** the seam MUST preserve existing dispatch, idempotency, risk gate, timing, finalize, and request-context behavior
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, desktop primitive, live readiness, or production trading behavior

