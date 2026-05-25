## Why

`catalog validate` already exposes selected bundle step counts by source, name, entry, source-name, option key, and labels. It also now exposes task/report-specific `source:entry` counts. The general selected-bundle view still lacks the same source-entry join, which makes it harder to audit which catalog source owns repeated step entries without reading full bundle definitions.

## What Changes

- Add additive `bundle_step_source_entry_counts`.
- Derive each key from selected resolved bundle steps as `source:entry`.
- Preserve summary view behavior by projecting the same read-only count map.

## Impact

- No catalog entry, task, report, trade command, or bundle step execution.
- No workflow-builder behavior or trading readiness claim.
- Existing payloads remain backward compatible; the field is additive.
