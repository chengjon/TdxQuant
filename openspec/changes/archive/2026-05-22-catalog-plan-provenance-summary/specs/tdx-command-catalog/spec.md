## ADDED Requirements

### Requirement: Command catalog plan and preview SHALL expose non-execution provenance
The command catalog `plan` and `preview` workflows SHALL include machine-readable provenance and non-execution constraint metadata for entry and bundle targets without mutating runtime catalog schemas or changing `catalog run` execution semantics.

#### Scenario: Caller plans a catalog entry with provenance
- **WHEN** a caller executes `catalog plan --entry <name>`
- **THEN** the result includes provenance metadata with `mode`, `target_type`, `target_name`, and `catalog_path`
- **AND** the result includes constraints stating that execution mode is non-executing and dispatch was not executed
- **AND** the underlying catalog entry dispatch workflow is not invoked

#### Scenario: Caller previews a catalog bundle summary with provenance
- **WHEN** a caller executes `catalog preview --bundle <name>` with `--view summary`
- **THEN** the selected output payload includes provenance metadata with `mode`, `target_type`, `target_name`, `catalog_path`, and `bundle_path`
- **AND** the selected output payload includes constraints stating that dispatch was not executed, schema files were not mutated, and run semantics were not changed
- **AND** the underlying bundle dispatch workflow is not invoked

#### Scenario: Catalog run behavior is unchanged
- **WHEN** a caller executes `catalog run` for an entry or bundle
- **THEN** the existing run dispatch semantics remain unchanged
- **AND** the provenance and constraint metadata added for non-executing plan/preview workflows does not change runtime catalog or bundle JSON schemas
