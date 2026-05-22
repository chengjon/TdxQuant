## Why

`FUNCTION_TREE.md` marks the catalog preview/discovery area as partial because callers can plan or preview entries and bundles, but the output still does not explicitly state the provenance and non-execution boundary of those results. This makes the feature registry harder to audit: readers can see that catalog preview exists, but not what evidence proves it stayed read-only and schema-preserving.

## What Changes

- Add machine-readable provenance metadata to `catalog plan` and `catalog preview` results for both entry and bundle targets.
- Add machine-readable non-execution constraints to the same result payloads so summary and detailed views state that dispatch was not executed, schema files were not mutated, and `catalog run` semantics were not changed.
- Keep runtime catalog and bundle JSON schemas unchanged.
- Keep `catalog run` behavior unchanged.
- Update `FUNCTION_TREE.md` E-10 as the single feature registry entry for the improved catalog preview/discovery boundary.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: catalog plan/preview payloads expose provenance and non-execution constraints without changing run behavior or runtime catalog schema.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected tests: `tests/test_api_cli.py`.
- Affected docs/specs: `FUNCTION_TREE.md`, `openspec/specs/tdx-command-catalog/spec.md`.
- No new external dependencies, migrations, or runtime catalog schema changes.
