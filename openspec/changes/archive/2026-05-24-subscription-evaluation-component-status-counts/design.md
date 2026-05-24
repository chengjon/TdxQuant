## Design

`_build_subscription_watch_governance_evaluation_summary()` already iterates over heartbeat, watermark, and reconnect summaries and classifies each component as fresh, stale, or not evaluated. The new field is derived in that loop and returned as a deterministic map sorted by key.

Expected examples:

- no explicit thresholds: `{"not_evaluated": 3}`
- heartbeat stale, watermark fresh, reconnect not evaluated: `{"fresh": 1, "not_evaluated": 1, "stale": 1}`

Summary views already deep-copy `governance.evaluation_summary`, so HTTP and CLI summary tests will assert that the new count map is preserved without adding full raw payloads.

## Risks

- The field duplicates existing list/count data. This is intentional for compact registry evidence; `FUNCTION_TREE.md` will state that it is not a health guarantee or automation trigger.
