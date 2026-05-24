# Design

## Context

Subscription watch status already carries detailed advisory governance data in the full payload: `governance.reasons`, `governance.actions`, `governance.action_summary`, and `governance.evaluation_summary`. HTTP and CLI summary views intentionally reduce that payload. They now include bounded reason samples, but action visibility is limited to aggregate fields such as count and primary action.

## Goals

- Expose representative advisory actions in HTTP and CLI summary views.
- Keep the projection bounded, deterministic, and read-only.
- Omit verbose action descriptions from samples so the summary does not become the detailed payload.
- Preserve the existing `governance.action_summary`, `reason_samples`, and raw-payload omission behavior.

## Non-Goals

- Do not start, stop, restart, reconnect, backoff, or manage subscription workers.
- Do not expose the full `governance.actions` list in summary view.
- Do not change the detailed status payload contract.
- Do not change event-stream or SSE behavior.

## Decisions

### 1. Sample compact action fields only

Each action sample will include `action`, `reason`, and `severity` when present. It will not include `description`, because description text belongs to the full detailed governance payload.

### 2. Use the same sample limit as reason samples

HTTP and CLI summary views already use a limit of three reason samples. Action samples use the same bounded count to keep the reduced summary predictable.

### 3. Compute samples in view builders

The detailed `status_summary` remains unchanged. HTTP and CLI summary builders derive action samples from the detailed `governance.actions` list, matching the existing reason-sample projection approach.

## Risks / Trade-offs

- Action samples can be mistaken for executable instructions. The summary continues to carry `governance.boundary` and advisory `action_summary`; tests also assert that full `actions` remains omitted.
- Compact samples omit descriptions by design, so operators needing full explanation must use the detailed payload.

