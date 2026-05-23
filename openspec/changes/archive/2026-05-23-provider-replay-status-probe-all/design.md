## Context

`provider-replay status` already accepts separate probe flags:

- `--probe-health`
- `--probe-watch-status`
- `--probe-watch-events`
- `--probe-watch-stream`

Each probe is opt-in and read-only. The status command delegates to existing probe helper functions and then builds the lifecycle boundary output.

## Design

Add a parser flag:

- `--probe-all`

In the status handler, compute booleans equivalent to:

- `probe_health = args.probe_health or args.probe_all`
- `probe_watch_status = args.probe_watch_status or args.probe_all`
- `probe_watch_events = args.probe_watch_events or args.probe_all`
- `probe_watch_stream = args.probe_watch_stream or args.probe_all`

Then reuse the existing helper calls and `args.probe_timeout`. No provider transport code changes are required.

## Boundaries

- No new HTTP endpoint or probe helper is introduced.
- No serving process is started.
- No daemon lifecycle management is added.
- Individual probe flags remain available for narrow checks.
