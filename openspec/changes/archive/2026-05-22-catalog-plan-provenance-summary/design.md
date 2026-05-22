## Context

The catalog CLI already supports `list`, `plan`, `preview`, and `run`. `plan` and `preview` resolve entry or bundle targets without dispatching the underlying workflow, and `--view summary` trims the output into a stable reduced payload. Earlier work added discovery metadata to list output, but plan/preview output still lacks a compact declaration of where the resolved catalog data came from and which execution boundaries were observed.

## Goals / Non-Goals

**Goals:**

- Add deterministic provenance metadata to entry and bundle plan/preview results.
- Add deterministic non-execution constraints to detailed and summary views.
- Make the metadata explicit enough for `FUNCTION_TREE.md` evidence without relying on prose-only interpretation.
- Preserve current CLI argument behavior and dispatch behavior.

**Non-Goals:**

- Do not change `runtime/command-catalog.json` or `runtime/command-bundles.json` schema.
- Do not change `catalog run` behavior.
- Do not introduce a workflow builder, editor, or runtime mutation path.
- Do not add new business task/report/broker capabilities.

## Decisions

- Build provenance inside the existing plan/preview result construction path in `tdxquant/cli.py`.
- Include `mode`, `target_type`, `target_name`, and `catalog_path` for all plan/preview results.
- Include `bundle_path` for bundle plan/preview results.
- Add a small constraints payload with `execution_mode: non_executing`, `dispatch_executed: false`, `schema_mutation: false`, and `run_semantics_changed: false`.
- Copy provenance and constraints into the summary view when present, rather than recomputing them during output selection.

## Risks / Trade-offs

- Absolute local paths are useful audit evidence but may vary by checkout. Tests should assert stable suffixes rather than whole machine-specific paths.
- Metadata names become part of the CLI payload contract, so the shape should stay small and conservative.
