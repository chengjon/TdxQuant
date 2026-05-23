## 1. Watermark Staleness Tests

- [x] 1.1 Add status-summary tests for watermark fresh/stale/not-evaluated behavior.
- [x] 1.2 Add bridge HTTP/registry forwarding tests for `watermark_stale_after_seconds`.
- [x] 1.3 Add CLI parser/dispatch tests for `--watermark-stale-after-seconds`.

## 2. Watermark Staleness Implementation

- [x] 2.1 Add watermark stale evaluation to summary/controller.
- [x] 2.2 Forward the threshold through bridge HTTP, registry, and CLI watch-status.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming lifecycle automation.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.
