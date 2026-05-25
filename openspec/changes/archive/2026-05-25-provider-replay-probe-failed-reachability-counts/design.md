## Design

`_build_provider_replay_probe_summary` already derives reachability buckets for requested probes as `reachable`, `unreachable`, or `unknown`. Add a second map, `failed_reachability_counts`, and increment it only in the existing non-healthy requested-probe branch that also feeds `failed`, `unhealthy`, and `failed_status_counts`.

The returned payload will include a sorted `failed_reachability_counts` object. When there are no requested non-healthy probes, the field is an empty object. Healthy probes and `not_requested` probes are excluded so the field remains a failed-only diagnostic.

## Boundary

This is a derived summary field over already-collected probe objects. It does not request additional endpoints, expose full probe payloads, inspect token or allowlist details, start a replay server, mutate provider state, or manage daemon lifecycle. It is not a health guarantee and does not replace `failed`, `failed_count`, `failed_status_counts`, or `requested_reachability_counts`.
