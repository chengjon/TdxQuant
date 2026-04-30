## ADDED Requirements

### Requirement: Task management SHALL support multi-method OR filtering for stable trade-audit daily and period workflows
The system SHALL allow the stable trade-audit daily and period workflows to filter immutable audit artifacts by either one method or a set of methods using OR semantics while preserving current single-method calls.

#### Scenario: Caller requests a trade-audit report with multiple methods
- **WHEN** a caller executes the stable trade-audit daily or period workflow with `methods=[buy_submit_once, confirm_current]`
- **THEN** the workflow MUST include entries whose trade-audit method matches any listed method and exclude entries outside that set

#### Scenario: Caller mixes single-method and multi-method filters
- **WHEN** a caller executes the stable trade-audit daily or period workflow with both `method` and `methods`
- **THEN** the workflow MUST reject the request as invalid instead of guessing precedence
