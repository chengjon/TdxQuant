## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn readiness manifest sample evidence without status promotion

`FUNCTION_TREE.md` SHALL cite the PingAn readiness manifest sample and catalog/task registration as partial evidence only.

#### Scenario: D-07 and D-08 cite manifest sample registration while remaining partial

- **GIVEN** D-07 and D-08 describe PingAn desktop trading readiness
- **WHEN** the PingAn readiness manifest sample registry is added
- **THEN** D-07 and D-08 SHALL remain `[部分实现]`
- **AND** their evidence SHALL cite `runtime/pingan/promotion-readiness-manifest.example.json`
- **AND** their evidence SHALL cite `plan-pingan-promotion-readiness`
- **AND** their evidence SHALL cite the OpenSpec change `pingan-promotion-readiness-manifest-sample-registry`
- **AND** their boundary SHALL say the entry is read-only discovery/registration evidence
- **AND** their boundary SHALL say the sample does not execute broker, desktop, trade, report, task, or bundle workflows
- **AND** their boundary SHALL say the sample does not prove production readiness or implemented status.
