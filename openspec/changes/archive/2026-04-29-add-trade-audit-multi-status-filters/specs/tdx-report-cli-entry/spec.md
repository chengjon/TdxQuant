## ADDED Requirements

### Requirement: Report and task CLI SHALL expose multi-status trade-audit filtering without breaking existing single-status calls
The system SHALL expose a stable CLI way to express multi-status trade-audit filtering for the existing daily and period workflows while preserving the current single-status option.

#### Scenario: Caller passes repeated multi-status arguments
- **WHEN** a caller invokes the stable trade-audit daily or period CLI workflow and repeats the multi-status argument
- **THEN** the CLI MUST forward the collected statuses into the existing stable workflow using OR semantics

#### Scenario: Caller mixes single-status and multi-status CLI arguments
- **WHEN** a caller invokes the stable trade-audit daily or period CLI workflow with both single-status and multi-status arguments
- **THEN** the CLI MUST reject the request as invalid instead of guessing precedence
