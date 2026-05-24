## Design

`_build_provider_replay_status_summary_view()` already reads the detailed `capabilities.endpoints` list to produce endpoint count and bounded samples. This change adds a small helper that maps each endpoint into a stable family name and returns sorted counts:

- endpoints under `/provider/v1/replay/watch/...` count as `watch`;
- all other endpoints under `/provider/v1/replay/...` count as `core`;
- non-string or unrelated endpoint values count as `other`.

The summary view includes only the aggregate object. It continues to omit the full `endpoints` list and bearer/allowlist/fixture path details.

## Boundaries

- This is a read-only projection from existing status metadata.
- It does not add, remove, or execute replay endpoints.
- It does not start, stop, restart, daemonize, supervise, schedule, or probe unless explicit probe flags are provided.
- It does not imply live Windows provider readiness or daemon lifecycle management.

## Verification

- Add focused CLI coverage for the new summary field.
- Run `python -m pytest tests/test_api_cli.py tests/test_provider_transport_replay.py -q`.
- Run `openspec validate --all --strict`.
- Run `git diff --check`.
- Run `python scripts/validate_function_tree_registry.py`.
