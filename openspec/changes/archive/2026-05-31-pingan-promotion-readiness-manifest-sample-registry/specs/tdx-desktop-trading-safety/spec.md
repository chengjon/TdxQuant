## ADDED Requirements

### Requirement: PingAn readiness manifest sample SHALL NOT satisfy live trading promotion gates

The sample manifest and its catalog/task registration SHALL be treated as discovery and wiring evidence only.

#### Scenario: Sample manifest registration remains below live readiness

- **GIVEN** a sample manifest is registered for PingAn promotion readiness rollup
- **WHEN** maintainers inspect the sample through task presets or command catalog planning
- **THEN** the sample SHALL NOT mark provider ownership as complete
- **AND** the sample SHALL NOT mark desktop lifecycle control as complete
- **AND** the sample SHALL NOT mark audit evidence as complete
- **AND** the sample SHALL NOT mark live manual acceptance as complete
- **AND** the sample SHALL NOT satisfy D-07 or D-08 implemented status by itself.
