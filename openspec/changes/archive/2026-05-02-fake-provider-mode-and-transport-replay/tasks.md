## 1. Replay Provider Core

- [x] 1.1 Add a replay-provider helper module that resolves default fixtures, explicit fixture names, and explicit fixture paths for supported capabilities.
- [x] 1.2 Add strict replay-mode validation so unsupported capabilities, missing fixtures, and malformed fixture assets fail deterministically without live fallback.
- [x] 1.3 Add replay helpers for synchronous provider results and replay source metadata normalization.

## 2. Manager And CLI Integration

- [x] 2.1 Extend `TdxApiManager` construction/configuration with replay provider mode and fixture selector options.
- [x] 2.2 Route supported synchronous capabilities through replay execution when replay mode is enabled while preserving current manager metadata and provider result contracts.
- [x] 2.3 Extend supported CLI entrypoints with replay-mode flags and argument validation for fixture name/path selection.

## 3. Subscription Watch Replay

- [x] 3.1 Add replay-mode materialization for `subscription-watch` using built-in completed-run fixtures.
- [x] 3.2 Support explicit replay manifest/directory sources for `subscription-watch` and rewrite run identity/output paths for the materialized run.
- [x] 3.3 Ensure replay-mode `subscription-watch` returns the current completed task contract without opening a live runtime subscription session.

## 4. Verification And Documentation

- [x] 4.1 Add or update replay fixtures, manager tests, CLI tests, and task tests covering default replay selection, explicit overrides, and no-live-fallback behavior.
- [x] 4.2 Update replay-mode and subscription-watch documentation to describe supported capabilities, fixture selection, and replay boundaries.
- [x] 4.3 Run targeted pytest coverage and strict OpenSpec validation for `fake-provider-mode-and-transport-replay`.
