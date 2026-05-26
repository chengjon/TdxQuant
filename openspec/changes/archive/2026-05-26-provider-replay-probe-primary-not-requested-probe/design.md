## Design

`_build_provider_replay_probe_summary` already builds an ordered `not_requested` list using the fixed probe key order. Add `primary_not_requested_probe` to the returned summary as the first item from that list, or `None` when all supported probes were requested.

The field is a compact coverage navigation hint. It does not replace `not_requested`, `not_requested_count`, or `request_coverage_status`, and it does not request or execute the missing probe target.

## Boundary

This is a derived summary field over already-collected probe objects. It does not request additional endpoints, expose full probe payloads, inspect token or allowlist details, start a replay server, mutate provider state, or manage daemon lifecycle. `None` only means the current summary has no not-requested probe in the existing list.
