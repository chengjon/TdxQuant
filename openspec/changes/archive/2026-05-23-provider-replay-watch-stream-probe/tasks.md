## 1. Probe Tests

- [x] 1.1 Add provider replay unit coverage for a healthy watch-stream probe and status runtime projection.
- [x] 1.2 Add CLI parse coverage for `provider-replay status --probe-watch-stream`.
- [x] 1.3 Add CLI handler coverage showing the watch-stream probe is opt-in and no serving is started.

## 2. Runtime Implementation

- [x] 2.1 Add a watch-stream probe helper for `/provider/v1/replay/watch/events/stream`.
- [x] 2.2 Add `watch_stream_probe` to `build_provider_transport_replay_status()`.
- [x] 2.3 Wire `--probe-watch-stream` through the provider-replay status command.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle management.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.
