## 1. Discovery Payload Hardening

- [x] 1.1 Harden the capability registry payload so `runtime.capabilities` always returns stable capability rows plus fixed `summary` and `grading` structures.
- [x] 1.2 Harden the health snapshot builder so `runtime.health` always returns stable `context`, `checks`, `warnings`, and compatibility `recommended_actions` fields.
- [x] 1.3 Add structured `recommended_action_items` with stable machine-readable identifiers, severities, and related-check linkage while preserving the legacy string action list.
- [x] 1.4 Harden `runtime.doctor` findings so each finding uses stable machine-readable identifiers and structured linkage to related checks or recommended actions.

## 2. Fixtures and Contract Tests

- [x] 2.1 Refresh discovery replay fixture assets and registry entries so capability registry, health, and doctor snapshots cover the hardened payload schema.
- [x] 2.2 Add or update manager and CLI tests to lock the hardened discovery payload fields and diagnostic-success semantics.
- [x] 2.3 Add or update replay fixture tests so discovery fixtures are treated as stable contract snapshots, including structured action rows.

## 3. Documentation

- [x] 3.1 Update discovery contract documentation to describe stable registry summary/grading fields, structured action rows, and stable finding identifiers.
- [x] 3.2 Update replay fixture documentation to describe the hardened discovery snapshots and any new fixture names or structured fields.

## 4. Validation

- [x] 4.1 Run the targeted discovery contract test suite covering manager, CLI, and replay fixture behavior.
- [x] 4.2 Run `openspec validate provider-capability-discovery-hardening --type change --strict` and resolve any artifact issues.
