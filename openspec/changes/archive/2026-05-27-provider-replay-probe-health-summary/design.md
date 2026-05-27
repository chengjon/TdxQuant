# provider replay probe health summary design

## Design

`runtime.probe_summary.health_summary` is emitted by provider replay status. It is a compact rollup of existing fixed-probe health fields and contains no full probe payloads, error samples, endpoint response bodies, daemon controls, or executable instructions.

Shape:

```json
{
  "status": "degraded",
  "healthy_count": 3,
  "failed_count": 1,
  "unhealthy_count": 1,
  "status_key_count": 2,
  "primary_healthy_probe": "health_probe",
  "primary_failed_probe": "watch_stream_probe",
  "primary_unhealthy_probe": "watch_stream_probe"
}
```

Rules:

- The object is derived from the same fixed probe list and sibling fields as `runtime.probe_summary`.
- Existing sibling fields remain available for compatibility.
- No-probe status reports `status=not_requested`, zero health/failure counts, and null primary health/failure probes.
- The object does not start sockets, schedule restarts, manage daemon lifecycle, execute unrequested probes, or enable write behavior.

## Boundaries

This change does not add background daemon lifecycle management, process supervision, automatic restart/backoff policy, live Windows provider integration, probe execution beyond explicitly requested probes, endpoint payload disclosure, or any provider write capability. It is an additive non-executing status projection.
