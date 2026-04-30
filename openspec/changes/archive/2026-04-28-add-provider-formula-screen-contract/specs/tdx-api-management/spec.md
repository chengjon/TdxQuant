## ADDED Requirements

### Requirement: Query API management SHALL expose a stable formula screen action
The system SHALL expose a stable `formula.screen(...)` action through `TdxApiManager.formula` in addition to the existing raw batch formula methods.

#### Scenario: Caller invokes formula screen through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke normalized stock-screen execution through `manager.formula.screen(...)`

#### Scenario: Raw batch formula method remains available
- **WHEN** a caller still needs the existing batch formula raw result shape
- **THEN** the manager MUST continue to expose `manager.formula.process_mul_xg(...)` alongside the new stable `manager.formula.screen(...)` action
