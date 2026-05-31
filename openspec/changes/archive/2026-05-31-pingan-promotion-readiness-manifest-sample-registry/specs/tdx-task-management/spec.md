## ADDED Requirements

### Requirement: PingAn promotion readiness rollup preset SHALL resolve a safe sample manifest

The task preset registry SHALL provide a stable read-only preset for the PingAn promotion readiness rollup sample manifest.

#### Scenario: Task preset resolves the sample manifest path

- **GIVEN** the task preset registry contains `plan-pingan-promotion-readiness`
- **WHEN** an operator invokes `task run --preset plan-pingan-promotion-readiness`
- **THEN** the preset SHALL resolve to task command `pingan-promotion-readiness-rollup`
- **AND** the preset SHALL use API profile `safe_read`
- **AND** the preset SHALL provide `evidence_manifest_path` pointing at the sample manifest
- **AND** the preset SHALL NOT provide a default `json_output_path`
- **AND** direct preflight, dialog readiness, and acceptance coverage paths SHALL remain unset unless the caller explicitly overrides them.

#### Scenario: Sample preset registration remains read-only by default

- **GIVEN** the sample preset points at an example manifest
- **WHEN** the preset is resolved for catalog planning or parser dispatch tests
- **THEN** no provider, desktop, trade, report, or bundle workflow SHALL be executed as part of preset discovery.
