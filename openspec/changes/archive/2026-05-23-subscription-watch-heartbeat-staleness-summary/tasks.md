## 1. Status Summary

- [x] 1.1 Add failing tests for opt-in heartbeat stale/fresh summary evaluation and default non-evaluation.
- [x] 1.2 Implement heartbeat staleness evaluation in the summary builder and controller status path.

## 2. Bridge Surface

- [x] 2.1 Add failing bridge HTTP, registry, and CLI tests for forwarding `heartbeat_stale_after_seconds`.
- [x] 2.2 Implement threshold query/route/CLI forwarding without changing default watch-status behavior.

## 3. Registry Documentation

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- [x] 3.2 Validate OpenSpec, focused tests, whitespace checks, and the FUNCTION_TREE status validator.
- [x] 3.3 Archive the OpenSpec change and re-run verification.
