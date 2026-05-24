# Design

## Context

`build_provider_transport_replay_status()` already includes the full read-only endpoint list in the detailed status payload under `capabilities.endpoints`. The CLI summary builder reduces that into `endpoint_count` so callers can detect the size of the replay surface without depending on the detailed schema.

## Goals

- Expose a small representative endpoint sample set in the summary view.
- Preserve `endpoint_count` and the existing omission of full `endpoints`.
- Keep the sample projection deterministic and derived only from existing detailed status.
- Avoid any serve/probe/lifecycle behavior changes.

## Non-Goals

- Do not add new replay HTTP endpoints.
- Do not start, stop, restart, daemonize, schedule, or supervise the replay service.
- Do not expose the full endpoint list in summary view.
- Do not prove that a replay server is currently running.

## Decisions

### 1. Sample from existing detailed status endpoints

The summary builder will derive samples from `status["capabilities"]["endpoints"]`, matching the source already used for `endpoint_count`.

### 2. Use a bounded sample limit of three

Three endpoints are enough to make the surface recognizable while keeping the summary reduced. The truncated flag tells callers when the detailed payload has more endpoints.

### 3. Keep endpoint samples inside `capabilities`

The samples describe the replay capability surface, so they belong next to `read_only`, `writes_supported`, and `endpoint_count`.

## Risks / Trade-offs

- Endpoint samples can be mistaken for a complete list. The summary includes `endpoint_sample_limit` and `endpoint_sample_truncated`, and `FUNCTION_TREE.md` will state the boundary explicitly.
- Endpoint samples do not prove the replay service is reachable. Runtime reachability remains represented by explicit probe fields.

