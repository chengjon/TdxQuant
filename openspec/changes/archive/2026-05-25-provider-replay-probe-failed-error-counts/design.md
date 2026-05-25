## Context

`_build_provider_replay_probe_summary()` already derives `failed`, `failed_status_counts`, and `error_code_counts` from the existing probe objects. `error_code_counts` is intentionally broad and counts any probe object with a string `error_code`.

The new field is a narrower failed-only rollup. It is derived after the probe is known to be requested and non-healthy, so it aligns with the existing `failed` target list and `failed_count`.

## Goals / Non-Goals

- Add deterministic `runtime.probe_summary.failed_error_code_counts`.
- Keep no-request and healthy-only summaries empty.
- Include failed-only counts in CLI summary view through existing `probe_summary` projection.
- Do not add new probe endpoints, retry behavior, daemon start/stop, socket management, or live provider lifecycle behavior.
- Do not replace individual probe payloads or full `error_code_counts`.

## Decisions

- Count only string `error_code` values.
- Count only after excluding `not_requested` probes and after classifying the requested probe as non-healthy.
- Sort keys before returning for deterministic JSON output.

## Risks / Trade-offs

- The field overlaps with `error_code_counts` when all error codes are already on failed probes. The narrower field is still useful because it states the failure-scoped interpretation explicitly.
