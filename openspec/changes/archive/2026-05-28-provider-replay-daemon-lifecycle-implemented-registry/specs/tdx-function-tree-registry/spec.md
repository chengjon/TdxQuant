## MODIFIED Requirements

### Requirement: FUNCTION_TREE lifecycle material status SHALL be explicitly bounded

The FUNCTION_TREE registry SHALL allow lifecycle-related feature nodes to be marked implemented when their evidence, tests, and boundaries describe the implemented lifecycle surface without implying downstream runtime availability.

#### Scenario: Provider replay daemon fake provider lifecycle node is implemented with bounded evidence

- **WHEN** E-06 cites replay fake provider HTTP, probe, managed daemon control, statefile ownership, supervisor, restart/backoff, process ownership diagnostics, managed lifecycle status, managed lifecycle readiness, tests, and OpenSpec evidence
- **THEN** E-06 MAY be registered as `[已实现]`
- **AND** the node boundary MUST state that implementation is limited to replay fake provider lifecycle management
- **AND** the node boundary MUST NOT imply live TongDaXin provider availability, broker readiness, workflow readiness, write support, or production trading readiness.

#### Scenario: Provider replay implemented status does not affect trading or subscription nodes

- **WHEN** E-06 is registered as `[已实现]`
- **THEN** D-07, D-08, B-16, E-09, and other feature nodes MUST retain their own explicit statuses, evidence, and boundaries.
