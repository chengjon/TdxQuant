## Context

The detailed provider replay status payload contains a `capabilities` object
with `read_only`, `writes_supported`, and the replay HTTP endpoints. Summary
mode currently focuses on lifecycle and probe rollups. For E-06, summary mode
should also make the no-write fake-provider boundary visible while staying
compact and non-executing.

## Goals / Non-Goals

- Add a compact status summary `capabilities` projection.
- Include only `read_only`, `writes_supported`, and `endpoint_count`.
- Avoid copying the full endpoint list into summary mode.
- Do not add daemon start/stop, write support, live provider support, probes by default, or socket startup behavior.

## Decisions

- Use an `endpoint_count` instead of endpoint names.
  - Rationale: it proves the summary is derived from detailed capabilities without making summary mode a duplicate of detailed status.
  - Alternative considered: copy `capabilities.endpoints`. That would make summary output grow with endpoint inventory and blur the reduced-view boundary.
- Keep the projection inside `summary_view`.
  - Rationale: default detailed status remains unchanged and backward compatible.

## Risks / Trade-offs

- Consumers may treat capability summary as runtime availability. Mitigation: keep existing runtime/probe fields and FUNCTION_TREE boundary text explicit that default status does not observe a running service.

## Migration Plan

No migration is required. The field is additive and only appears in opt-in status summary view.

## Open Questions

None.
