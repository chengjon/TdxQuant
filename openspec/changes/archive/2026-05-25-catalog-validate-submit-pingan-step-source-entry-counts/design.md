## Design

`_validate_catalog_registry` already accumulates submit-once and PingAn step entry counts while walking resolved steps. Extend those same branches to build source-qualified maps when both `source` and `entry` are string, non-empty values.

The summary view should deep-copy both maps from detailed validation. These maps are aggregate coverage metadata, not a complete step manifest.

## Boundary

- Count only selected resolved bundles in the submit-once or PingAn subset.
- Count only resolved steps with string, non-empty `source` and `entry`.
- Format keys as `<source>:<entry>`.
- Do not expose full bundle step manifests.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not claim broker readiness, execution coverage, workflow readiness, or trade safety.
