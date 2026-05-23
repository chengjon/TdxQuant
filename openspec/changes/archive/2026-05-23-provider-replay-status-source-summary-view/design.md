## Context

The detailed provider replay lifecycle status contains:

- `replay_source.source_kind`
- `replay_source.fixture`
- `replay_source.fixture_path`

The status summary view is intentionally compact and already avoids copying full endpoint details. Replay-source provenance has the same shape: callers need to know what kind of source was selected, but a compact summary does not need the full path string.

## Goals / Non-Goals

Goals:

- Expose compact replay-source provenance in `provider-replay status --view summary`.
- Preserve the detailed status payload as the place for full fixture path detail.
- Keep the summary view read-only and non-lifecycle-managing.

Non-goals:

- Do not start, stop, restart, supervise, or probe unless existing explicit probe flags request it.
- Do not resolve or validate new fixture types.
- Do not add a full fixture catalog to the status summary view.

## Decisions

1. Project bounded source metadata.

   The summary view copies `source_kind` and `fixture`, and derives `fixture_path_provided` from whether detailed `fixture_path` is present. It does not copy `fixture_path`.

2. Keep summary and detailed payload roles separate.

   Detailed status remains available under `data.status` and still contains complete `replay_source` detail. Summary view remains a reduced operator-facing projection.

## Risks / Trade-offs

- Additive fields are low compatibility risk.
- Omitting the full path means summary users still need detailed output when they need exact file provenance; this is intentional to keep summary compact.

## Migration Plan

No migration is required. Existing commands and flags remain unchanged.

## Open Questions

None.
