## Context

Catalog list/plan/run already resolve entries and bundles across task, report, and trade presets. Summary views exist, but callers still need to inspect detailed payloads to discover available labels, understand why a label matched, or request a non-executing preview with explicit preview semantics.

## Goals / Non-Goals

**Goals:**

- Add stable discovery metadata to list responses.
- Add `catalog preview` as a non-executing alias with explicit `mode: preview`.
- Keep summary-view output constrained and deterministic.
- Cover label and bundle discovery with focused tests.

**Non-Goals:**

- Do not change catalog or bundle JSON schema.
- Do not add new business capability contracts from catalog metadata.
- Do not change run execution semantics.
- Do not require live provider/trade access.

## Decisions

1. Implement preview at the CLI workflow layer.
   - Rationale: preview is a presentation/dispatch contract over existing plan resolution, not a new catalog schema concept.
   - Alternative considered: add `preview` fields into every runtime catalog entry. That would change the schema and make catalog metadata too authoritative.

2. Compute discovery metadata from resolved entries and bundles.
   - Rationale: labels already exist in the schema. The hardening should expose matched labels and available label counts without requiring schema changes.

3. Keep summary output reduced.
   - Rationale: callers that request `--view summary` need stable list/plan/preview fields, not full nested preset options.

## Risks / Trade-offs

- Existing detailed output remains larger than summary output -> summary callers should explicitly pass `--view summary`.
- Preview duplicates plan resolution behavior -> tests keep the two paths aligned while preserving separate `mode` metadata.
- Label discovery depends on current runtime labels -> tests should use the committed runtime catalog/bundle files rather than inventing a second schema.
