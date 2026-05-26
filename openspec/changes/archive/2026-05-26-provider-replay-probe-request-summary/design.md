# provider replay probe request summary design

## Design

`runtime.probe_summary.request_summary` is emitted by provider replay status. It is a compact rollup of existing fixed-probe request coverage fields and contains no full probe payloads, error samples, endpoint response bodies, daemon controls, or executable instructions.

Shape:

```json
{
  "status": "complete",
  "total_count": 4,
  "requested_count": 4,
  "not_requested_count": 0,
  "healthy_count": 3,
  "failed_count": 1,
  "unhealthy_count": 1,
  "primary_requested_probe": "health_probe",
  "primary_not_requested_probe": null
}
```

Rules:

- The object is derived from the same fixed probe list and sibling count fields as `runtime.probe_summary`.
- Existing sibling fields remain available for compatibility.
- No-probe status reports `status=none`, `requested_count=0`, and a stable primary not-requested probe.
- The object does not start sockets, schedule restarts, manage daemon lifecycle, execute unrequested probes, or enable write behavior.

## Boundaries

This change does not add background daemon lifecycle management, process supervision, automatic restart/backoff policy, live Windows provider integration, probe execution beyond explicitly requested probes, endpoint payload disclosure, or any provider write capability. It is an additive non-executing status projection.
