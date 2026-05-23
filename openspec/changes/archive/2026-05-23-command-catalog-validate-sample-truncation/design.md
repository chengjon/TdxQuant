## Context

E-11 tracks fixed task/report combo bundle entries in `FUNCTION_TREE.md`. `catalog validate` currently counts matching task/report bundles and keeps the first five deterministic sample ids. The boundary text correctly says this is not a complete bundle list, but the API payload itself lacks an explicit truncation marker.

## Goals / Non-Goals

Goals:

- Make the sample cap explicit in detailed validation data and summary view data.
- Keep the validation path non-executing.
- Keep samples deterministic and bounded.

Non-goals:

- Do not add a full bundle inventory endpoint.
- Do not add CLI flags to tune the sample limit.
- Do not execute task, report, trade, or bundle steps.
- Do not change catalog planning or runtime bundle semantics.

## Decisions

1. Use a named in-code sample limit for task/report bundle samples.

   The existing cap is five. Keeping that limit stable avoids payload growth while allowing callers to interpret the sample list correctly.

2. Add two additive fields to validation payloads.

   `task_report_bundle_sample_limit` records the cap used for representative samples. `task_report_bundle_sample_truncated` is true when `task_report_bundle_count` is greater than the number of returned samples. This keeps the payload self-describing without returning every bundle id.

3. Project the same fields into `--view summary`.

   Summary view is the compact view most likely to be used as registry evidence. It should expose the same boundary as the detailed validation object while still omitting full entry and bundle rows.

## Risks / Trade-offs

- The fields are additive, so existing callers that ignore unknown fields are unaffected.
- Callers that previously inferred completeness from sample length will now have an explicit truncation flag to consume.
- The fixed limit means callers still need catalog list/plan flows for full inspection.

## Migration Plan

No migration is required. Existing commands and flags remain unchanged.

## Open Questions

None.
