## Context

Detailed provider replay lifecycle status includes:

- `security.bearer_token_required`
- `security.source_allowlist_enabled`
- `security.master_allowlist_count`

The compact status summary currently omits these fields, even though they are part of the fake-provider boundary evidence. Summary users should not need the detailed payload only to know whether replay access is protected.

## Goals / Non-Goals

Goals:

- Project compact security boundary metadata in `provider-replay status --view summary`.
- Keep secrets and allowlist members out of the summary view.
- Preserve detailed status as the place for complete structured status data.

Non-goals:

- Do not expose token values.
- Do not expose allowlist member values.
- Do not start, stop, restart, supervise, or probe unless existing explicit probe flags request it.
- Do not change replay server authorization behavior.

## Decisions

1. Copy only scalar security boundary fields.

   Summary view copies the three existing scalar fields from detailed `security`: bearer-token requirement, whether allowlist enforcement is configured, and allowlist count.

2. Keep sensitive details out of compact output.

   The detailed status already avoids token values; the summary view will also avoid any allowlist members or token material.

## Risks / Trade-offs

- Additive scalar output is low compatibility risk.
- Summary users still need config files or detailed operational docs if they need exact allowlist contents; this is intentional.

## Migration Plan

No migration is required. Existing commands and flags remain unchanged.

## Open Questions

None.
