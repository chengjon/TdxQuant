# provider replay lifecycle control plan

## Why

E-06 has explicit lifecycle status, operation summaries, backoff, supervision, and statefile boundary metadata, but there is still no stable non-executing entry that lets an operator ask "what would a lifecycle control operation require?" without accidentally starting or stopping anything.

Adding `provider-replay lifecycle-plan` creates a read-only planning surface for start/stop/restart/backoff. It makes the current blocked state actionable and discoverable while preserving the boundary that real daemon control is not implemented.

## What Changes

- Add `provider-replay lifecycle-plan --config --operation {start,stop,restart,backoff}`.
- Return a detailed non-executing plan that references current lifecycle status, supervision, statefile, and blocked operation metadata.
- Add `--view summary` for compact plan output.
- Guarantee the command does not serve, probe, start, stop, restart, daemonize, supervise, inspect processes, or read/write lifecycle statefiles.
- Update focused CLI tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for API CLI/provider replay, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
