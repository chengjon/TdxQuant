# Proposal: Catalog Validate Task Report Step Count

## Why

`catalog validate` already reports task/report bundle count, bounded samples, step source counts, and label counts. Consumers can infer the total selected step footprint by summing `task_report_bundle_step_source_counts`, but the summary does not expose that scalar directly.

The catalog registry should make the task/report bundle step total explicit while preserving the non-executing validation boundary.

## What Changes

- Add `task_report_bundle_step_count` to catalog validation payloads.
- Include the same field in `catalog validate --view summary`.
- Derive the count only from resolved bundle step definitions that contain both task and report steps.

## Non-Goals

- Do not execute task, report, trade, or bundle steps.
- Do not add an arbitrary workflow builder.
- Do not expose a full bundle/step listing beyond existing detailed validation payloads and bounded samples.
