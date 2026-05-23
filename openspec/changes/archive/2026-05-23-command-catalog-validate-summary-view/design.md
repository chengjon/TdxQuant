# Design

## Context

`catalog list`, `catalog plan`, `catalog preview`, and `catalog run` already use the existing `--view summary` selector and `_select_catalog_output_payload()` to print a reduced payload when `summary_view` is present. `catalog validate` currently returns only detailed validation data.

The validation result already includes the core fields needed for a concise registry projection:

- selected kind, entry, bundle, and label
- entry, bundle, and task/report bundle counts
- invalid count, validity, and errors
- `non_execution: true`

## Approach

Extend the existing catalog summary projection path:

- Add `--view` to the `catalog validate` parser with the same `detailed|summary` choices and `detailed` default as other catalog commands.
- Teach `_build_catalog_summary_view()` to return a `mode: "validate"` projection when the result contains `validation`.
- Add the summary projection inside `_validate_catalog_registry()` for both successful and failed validation results.

The summary projection is intentionally count-oriented. It does not copy the full error list unless there are validation errors, and it does not expose resolved step internals.

## Boundaries

- `catalog validate --view summary` remains non-executing.
- It does not alter catalog entry or bundle JSON schemas.
- It does not change `catalog validate` default detailed output.
- It does not add new task/report/trade semantics or compose new bundles.
