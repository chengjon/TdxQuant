## 1. Replay Transport Service

- [x] 1.1 Add focused failing tests for replay HTTP health/catalog/synchronous result endpoints.
- [x] 1.2 Implement a minimal fixture-backed provider transport replay HTTP service with daemon-style bearer/allowlist checks.
- [x] 1.3 Ensure synchronous replay responses preserve existing provider result contracts and never fall back to live runtime.

## 2. Subscription Watch Fake Provider

- [x] 2.1 Add focused failing tests for replay watch status, event rows, and SSE frame endpoints.
- [x] 2.2 Implement read-only subscription-watch fake provider projections from built-in or caller-supplied replay fixtures.
- [x] 2.3 Add deterministic delayed playback metadata for stream frames while keeping immediate playback as the default.

## 3. Fixtures And Documentation

- [x] 3.1 Add delayed playback replay fixture sample and catalog descriptor metadata.
- [x] 3.2 Update `FUNCTION_TREE.md` and relevant specs to reflect transport replay as partial/offline capability, not live provider evidence.

## 4. Verification

- [x] 4.1 Run focused replay transport tests.
- [x] 4.2 Run strict OpenSpec validation for the change and all specs.
- [x] 4.3 Run `git diff --check`.
