## Design

`_build_provider_replay_probe_summary()` already classifies fixed probe keys into requested, healthy, unhealthy, and not-requested groups. Because `failed_count` is currently derived from the unhealthy group, `failed` will be an additive list using the same fixed probe key order and the same classification.

Summary views already include a deep copy of `runtime.probe_summary`, so no separate summary-view transformation is required. Tests will assert that the summary view preserves `failed`.

## Risks

- `failed` duplicates the existing `unhealthy` list in the current status model. This is intentional naming alignment with `failed_count`; `FUNCTION_TREE.md` will explicitly describe it as a compact derived target list, not a new probe outcome model.
