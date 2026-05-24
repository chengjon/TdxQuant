# Proposal: Catalog Validate Bundle Step Count

## Why

`catalog validate` already reports bundle counts and task/report bundle step counts, but consumers cannot see the total step count for the selected bundle set without re-deriving it themselves. A derived `bundle_step_count` keeps the validation payload self-describing while remaining non-executing.

## What Changes

Add `bundle_step_count` to the catalog validation payload and summary view. The count is derived from the resolved bundle step lists already processed by validation.

## Out Of Scope

- No bundle execution or replay behavior changes.
- No workflow builder.
- No changes to task/report bundle samples or labels beyond the existing validation summaries.

## Success Criteria

- Validation reports `bundle_step_count`.
- Summary view mirrors the same `bundle_step_count`.
- `bundle_step_count` remains a derived scalar, not an execution proof.
