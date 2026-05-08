## 1. Provider Envelope Hardening

- [x] 1.1 Harden the shared synchronous provider envelope builder so manager-driven query and formula responses always emit `success`, `ok`, normalized `runtime`, array `warnings`, array `artifacts`, and object `data`.
- [x] 1.2 Update `TdxApiManager` synchronous result assembly to route query/formula responses through the hardened envelope behavior without breaking existing payload semantics such as profile metadata and `data.next_action`.
- [x] 1.3 Update `manager.runtime.capabilities(...)`, `manager.runtime.health(...)`, and `manager.runtime.doctor(...)` to use the same hardened envelope and preserve diagnostic-success semantics when the environment is degraded or unavailable.

## 2. CLI Contract Alignment

- [x] 2.1 Update `tdxquant api ...` JSON output paths to reuse the hardened synchronous provider serializer instead of command-local field assembly.
- [x] 2.2 Preserve non-zero exit codes for failed synchronous provider calls while ensuring the CLI still emits the full hardened provider JSON envelope on failure.

## 3. Fixtures, Tests, and Documentation

- [x] 3.1 Refresh provider replay fixture assets and loader expectations so bundled synchronous JSON fixtures cover success/failure query-formula snapshots plus `runtime.capabilities`, `runtime.health`, and `runtime.doctor`.
- [x] 3.2 Add or update tests for manager, CLI, and fixture contract coverage to lock `success`/`ok`, normalized container fields, timing/runtime metadata, and CLI failure-envelope behavior.
- [x] 3.3 Update provider result and discovery documentation to describe the hardened envelope, temporary `ok` compatibility alias, and CLI JSON/exit-code semantics.

## 4. Validation

- [x] 4.1 Run the targeted provider contract test suite and confirm the hardened synchronous envelope passes across manager, CLI, and replay fixture coverage.
- [x] 4.2 Run `openspec validate provider-result-contract-hardening --type change --strict` and resolve any proposal/design/spec/task contract issues.
