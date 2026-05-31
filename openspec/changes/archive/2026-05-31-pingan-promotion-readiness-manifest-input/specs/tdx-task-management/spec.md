## ADDED Requirements

### Requirement: Task management SHALL load PingAn promotion readiness evidence manifests

The task manager SHALL allow callers to supply a read-only evidence manifest for PingAn promotion readiness rollups.

#### Scenario: Caller provides manifest evidence paths

- **WHEN** a caller provides `evidence_manifest_path`
- **THEN** the task SHALL load preflight, dialog readiness, acceptance coverage, and freshness cutoff values from the manifest
- **AND** it SHALL build the existing read-only promotion readiness rollup from those resolved values
- **AND** the result SHALL include `evidence_manifest` metadata.

#### Scenario: Explicit arguments override manifest values

- **WHEN** the manifest provides an evidence value and the caller also provides the same value directly
- **THEN** the direct caller-provided value SHALL take precedence.

#### Scenario: Expected gate metadata is reported

- **WHEN** the manifest includes `expected_gates`
- **THEN** the rollup SHALL report expected gates and missing expected gates
- **AND** it SHALL NOT execute additional workflows to satisfy those gates.

