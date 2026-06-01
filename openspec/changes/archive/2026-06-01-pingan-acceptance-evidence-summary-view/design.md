## Context

The existing D-13 manager payload is intentionally detailed because it documents all boundaries and evidence categories. That is useful for human review but verbose for automation.

This change adds a CLI-level summary projection, following the existing pattern where commands keep detailed data while adding `summary_view` for compact machine reads.

## Goals / Non-Goals

Goals:

- Add `--view summary` to `trade acceptance-evidence`.
- Keep `--view detailed` as the default and preserve the detailed payload.
- Include only stable summary fields:
  - schema
  - target nodes
  - covered commands and methods
  - evidence category names
  - artifact target keys
  - side-effect flags
  - boundary

Non-goals:

- Do not add a new manager method.
- Do not execute or evaluate acceptance evidence.
- Do not change catalog planning behavior.
- Do not alter FUNCTION_TREE status.

## Verification

- Red tests for parser and `summary_view`.
- Focused and full `tests/test_api_cli.py`.
- `openspec validate --all --strict`.
- `git diff --check`.
- `python scripts/validate_function_tree_registry.py`.
