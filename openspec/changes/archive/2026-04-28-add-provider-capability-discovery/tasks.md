## 1. Discovery Contract Foundation

- [x] 1.1 Define the provider capability registry structure, grading literals, and shared discovery/probe helpers.
- [x] 1.2 Define the normalized health check payload and doctor finding payload so diagnostics can stay machine-readable even when the environment is unhealthy.
- [x] 1.3 Extend the provider result contract coverage and docs so discovery responses reuse the same synchronous envelope.

## 2. Runtime and Manager Integration

- [x] 2.1 Add bridge/runtime implementations for provider capability discovery, provider health, and provider doctor.
- [x] 2.2 Expose `capabilities`, `health`, and `doctor` through `RuntimeApi` and `TdxApiManager.runtime`.
- [x] 2.3 Add or update bridge and manager tests that lock success semantics, check structures, grading fields, and metadata attachment.

## 3. CLI Integration

- [x] 3.1 Add nested `api capabilities`, `api health`, and `api doctor` parser/dispatch support.
- [x] 3.2 Add flat `tdx-capabilities`, `tdx-health`, and `tdx-doctor` bridge-oriented commands.
- [x] 3.3 Ensure discovery/health/doctor CLI outputs use the provider result envelope and add coverage for structured output behavior.

## 4. Docs and Validation

- [x] 4.1 Document the new provider discovery contract and update roadmap references that previously treated discovery as future work.
- [x] 4.2 Run focused tests plus `python -m compileall tdxquant` and `openspec validate add-provider-capability-discovery --type change --strict`.
- [x] 4.3 Capture follow-up work needed for HTTP exposure, replay/fake fixtures, and subscription/formula contract expansion.
