## Design

`_build_provider_replay_probe_summary` already normalizes each requested probe's reachability as `reachable`, `unreachable`, or `unknown`. Add `healthy_reachability_counts` and increment it only in the existing healthy requested-probe branch that also feeds `healthy`, `healthy_count`, and `healthy_http_status_counts`.

The returned payload will include a sorted `healthy_reachability_counts` object. When there are no requested healthy probes, the field is an empty object. Failed and `not_requested` probes are excluded so the field remains a healthy-only diagnostic.

## Boundary

This is a derived summary field over already-collected probe objects. It does not request additional endpoints, expose full probe payloads, inspect token or allowlist details, start a replay server, mutate provider state, or manage daemon lifecycle. It is not a health guarantee and does not replace `healthy`, `healthy_count`, `requested_reachability_counts`, or single-probe evidence.
