## ADDED Requirements

### Requirement: Deferred plugin DLL material SHALL be reconciled as a bounded asset
The system SHALL reconcile the external `docs\TestPluginTCale` material through a separate bounded plugin/DLL asset change rather than by bulk-importing the external docs tree.

#### Scenario: Plugin sample is adopted after the main merge
- **WHEN** the external `D:\MyCode3\tdx\docs\TestPluginTCale` sample is adopted into the current repository
- **THEN** the adoption MUST remain curated and reviewable
- **AND** generated or user-local Visual Studio artifacts MUST be excluded
- **AND** the adoption MUST NOT broaden current runtime formula or trading capability claims
