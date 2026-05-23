# Tasks

## 1. Spec

- [x] Add worker bridge HTTP summary-view requirement and scenarios.

## 2. Tests

- [x] Cover default detailed `watch/status` response remains unchanged.
- [x] Cover `view=summary` compact response.
- [x] Cover invalid `view` values returning an invalid request failure.

## 3. Implementation

- [x] Add HTTP query parsing for `view=detailed|summary`.
- [x] Add summary projection helper for bridge HTTP status results.
- [x] Preserve stale-threshold forwarding and controller call behavior.

## 4. Registry And Verification

- [x] Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.
- [x] Run focused pytest, OpenSpec validation, diff check, registry validation,
  and GitNexus change detection.
