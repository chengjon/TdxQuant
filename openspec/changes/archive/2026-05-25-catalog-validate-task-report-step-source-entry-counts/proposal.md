## Why

`catalog validate` already exposes task/report bundle step counts by source, name, source-name, entry, option key, and labels. Operators can see which sources and entries appear, but cannot tell which source owns each repeated entry without reading the detailed bundle definitions.

## What Changes

- Add additive `task_report_bundle_step_source_entry_counts`.
- Derive each key from selected task/report bundle steps as `source:entry`.
- Preserve summary view behavior by projecting the same read-only count map.

## Impact

- No catalog entry, task, report, trade command, or bundle step execution.
- No new runtime preset, workflow builder, or trading surface.
- Existing validation payloads remain backward compatible; the field is additive.
