## ADDED Requirements

### Requirement: Task management SHALL gate PingAn promotion evidence freshness

The task manager SHALL allow the PingAn promotion readiness rollup to reject stale evidence artifacts when a freshness cutoff is provided.

#### Scenario: Fresh evidence remains eligible

- **WHEN** a caller supplies a freshness cutoff and evidence files are newer than the cutoff
- **THEN** the rollup SHALL preserve the existing gate status evaluation
- **AND** it SHALL report the evidence as fresh.

#### Scenario: Stale evidence remains visible but incomplete

- **WHEN** a caller supplies a freshness cutoff and one or more evidence files are older than the cutoff
- **THEN** the rollup SHALL mark the affected evidence stale
- **AND** it SHALL keep the affected gate incomplete
- **AND** it SHALL expose the stale evidence path and source kind.

#### Scenario: No freshness cutoff preserves existing behavior

- **WHEN** a caller omits the freshness cutoff
- **THEN** the rollup SHALL behave as the existing read-only evidence aggregator
- **AND** it SHALL not invent freshness failures.

