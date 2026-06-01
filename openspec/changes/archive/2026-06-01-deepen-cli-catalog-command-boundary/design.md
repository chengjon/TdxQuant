## Context

The catalog CLI surface is stable and already includes discovery, planning, preview, validation, summary views, and execution dispatch. Most of that logic currently lives in `tdxquant/cli.py`, which also owns many unrelated API, task, report, provider, and trade command groups.

The goal is architectural deepening, not a new workflow. Catalog users should see the same commands and payload contracts, while catalog command implementation becomes easier to test and evolve independently from the rest of the CLI.

## Goals / Non-Goals

**Goals:**

- Establish a dedicated catalog CLI command boundary for parser registration and subcommand handling.
- Preserve existing catalog command behavior and output shape.
- Keep `catalog list`, `catalog plan`, `catalog preview`, and `catalog validate` read-only.
- Keep `catalog run` on the existing execution path, without adding any new task/report/trade execution semantics.
- Add public-interface tests around catalog parser/handler behavior before moving code.

**Non-Goals:**

- No new catalog entry, bundle, preset, or runtime JSON schema.
- No workflow builder.
- No new task, report, trade, provider, or broker capability.
- No broad rewrite of all CLI command groups in this change.

## Decisions

1. Use a catalog-specific CLI boundary instead of a generic CLI plugin framework.

   Rationale: the immediate friction is catalog locality. A generic framework would expand scope and create migration risk across unrelated command groups.

   Alternative considered: introduce a top-level command registry for every CLI group now. Rejected for this change because it would touch API, task, report, trade, provider, and desktop commands at once.

2. Preserve `tdxquant/cli.py` as the process entrypoint.

   Rationale: callers and tests already import or execute `tdxquant.cli`. Keeping that entrypoint stable makes this a non-breaking architecture change.

   Alternative considered: move the whole CLI package entrypoint. Rejected because it would make import paths and command invocation semantics part of the migration.

3. Test through public parser and handler behavior.

   Rationale: this is a refactor boundary change. Tests should survive internal function moves and only fail if the observable catalog command surface changes.

   Alternative considered: assert private helper placement or direct helper calls. Rejected because that would make the tests implementation-coupled.

## Risks / Trade-offs

- Catalog helpers may still depend on shared CLI serialization/output helpers → move only what can be moved cleanly and keep shared helpers imported from `tdxquant.cli` until a later CLI-wide extraction.
- Import cycles between `tdxquant.cli` and a new catalog boundary module → use dependency injection for shared writer/manager hooks or keep wrapper functions in `tdxquant.cli` during the transition.
- Large existing catalog test coverage may hide accidental payload drift → add focused snapshot-style field assertions for list/plan/validate summary payloads and run existing `tests/test_api_cli.py`.

## Migration Plan

1. Add red tests for catalog parser/handler behavior that should remain stable after extraction.
2. Introduce the catalog CLI boundary module and route top-level catalog parser/handler calls through it.
3. Move catalog-specific helper logic that does not require broad CLI globals.
4. Run focused CLI tests and registry validation.
5. Update `FUNCTION_TREE.md` evidence and archive the OpenSpec change.
