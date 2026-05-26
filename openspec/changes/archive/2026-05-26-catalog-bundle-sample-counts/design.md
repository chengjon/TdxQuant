# Design: Catalog bundle sample counts

## Context

Catalog summary views intentionally project bounded sample arrays rather than full bundle manifests. Existing fields include sample arrays, sample limits, truncation flags, full bundle counts, and step counts for task+report, submit-once, and PingAn bundle subsets.

The remaining machine-readability gap is the visible sample size. Consumers can derive it from the arrays, but explicit sample count fields keep the contract aligned with other summary projections and make truncation checks direct.

## Goals / Non-Goals

- Goal: expose `task_report_bundle_sample_count` as `len(task_report_bundle_samples)`.
- Goal: expose `submit_once_bundle_sample_count` as `len(submit_once_bundle_samples)`.
- Goal: expose `pingan_bundle_sample_count` as `len(pingan_bundle_samples)`.
- Non-goal: expose full bundle manifests or option values.
- Non-goal: execute any catalog entry, bundle step, task/report command, submit-once command, broker probe, or trade operation.

## Decisions

- Derive each count from the already bounded visible sample array in the summary view.
- Leave full aggregate counts unchanged, including `*_bundle_count`, `*_bundle_step_count`, `*_bundle_sample_limit`, and `*_bundle_sample_truncated`.
- Keep the change additive and summary-only.

## Risks / Trade-offs

- The fields are redundant with array lengths, but explicit counts make downstream consumers simpler and align with current registry conventions.

## Migration Plan

No migration required. Existing catalog summary fields remain unchanged.

## Open Questions

None.
