## ADDED Requirements

### Requirement: Command catalog SHALL expose PingAn live/manual acceptance recorder discovery

The task catalog SHALL include a read-only discovery entry for the PingAn live/manual acceptance recorder.

#### Scenario: Catalog includes dry-run recorder preset

- **WHEN** callers list task catalog entries by label `manual-acceptance`
- **THEN** the catalog SHALL include `plan-pingan-live-manual-acceptance`
- **AND** the task preset SHALL run `pingan-live-manual-acceptance` in dry-run mode
- **AND** catalog plan/validate SHALL NOT execute the recorder or create artifacts.

