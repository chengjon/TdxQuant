## 1. OpenSpec Artifacts

- [x] 1.1 Create proposal, design, and spec deltas for architecture boundary hardening.
- [x] 1.2 Validate the change is apply-ready with OpenSpec.

## 2. Runtime Architecture Helpers

- [x] 2.1 Add capability risk classification metadata for query, provider mutation, native trade mutation, and desktop trade mutation surfaces.
- [x] 2.2 Add a central runtime configuration registry for project runtime JSON paths and object validation.
- [x] 2.3 Add focused tests for risk classification and runtime config registry behavior.

## 3. API CLI Boundary Extraction

- [x] 3.1 Add a dedicated API CLI module that owns nested `api` parser registration and dispatch.
- [x] 3.2 Make the root CLI delegate nested `api` parser construction and execution to the API CLI module without changing public command behavior.
- [x] 3.3 Add or update tests proving nested `api` command behavior still works through the root CLI and the extracted module.

## 4. Manager Call Envelope

- [x] 4.1 Add a shared `TdxApiManager` call envelope for profile metadata, timing, replay dispatch, and provider contract attachment.
- [x] 4.2 Migrate a small read-only manager slice to the envelope while preserving result payloads.
- [x] 4.3 Add focused tests for live and replay envelope behavior.

## 5. Validation

- [x] 5.1 Run focused architecture, API manager, and API CLI tests.
- [x] 5.2 Update OpenSpec task checkboxes and report final status.
