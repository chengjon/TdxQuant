# Tasks

## 1. Spec

- [x] Add provider replay probe-summary requirement and scenarios.

## 2. Tests

- [x] Cover default status where no probes were requested.
- [x] Cover healthy requested probes.
- [x] Cover degraded requested probes.

## 3. Implementation

- [x] Add a helper that derives `runtime.probe_summary` from normalized probes.
- [x] Keep individual probe payloads and lifecycle boundary fields unchanged.

## 4. Registry And Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence and boundary text.
- [x] Run focused pytest, OpenSpec validation, diff check, and registry validation.
