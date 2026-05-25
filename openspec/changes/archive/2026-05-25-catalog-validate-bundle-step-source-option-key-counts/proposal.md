## Why

`catalog validate` already exposes selected bundle step option-key counts and selected bundle step source counts. Consumers still need to correlate those maps manually to see which catalog source contributes an option key, and the full step manifest remains intentionally unavailable in summary output.

## What Changes

- Add additive `bundle_step_source_option_key_counts` to catalog validation payloads.
- Derive it from selected resolved bundle steps as `source:option_key`.
- Preserve summary-view projection without executing catalog entries, tasks, reports, trades, or bundle steps.

## Impact

- No catalog execution behavior changes.
- No new workflow-builder semantics or readiness claim.
- Existing consumers remain compatible because the field is additive.

