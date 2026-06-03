## ADDED Requirements

### Requirement: Provider replay mode SHALL remain strict behind architecture boundary helpers
The system SHALL keep replay-mode execution strict and fixture-backed when manager or provider helper boundaries are introduced.

#### Scenario: Shared manager envelope invokes replay for migrated method
- **WHEN** a migrated manager proxy method executes in replay mode with a known capability identity
- **THEN** the shared manager-call envelope MUST route to the existing replay fixture execution path
- **AND** it MUST NOT call live Windows runtime code

#### Scenario: Shared manager envelope returns stable unsupported replay failure
- **WHEN** a migrated manager proxy method executes in replay mode for an unsupported capability
- **THEN** the system MUST return the same class of stable unsupported replay failure as the existing replay dispatch path
- **AND** it MUST NOT fall back to live runtime execution
