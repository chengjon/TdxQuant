# Design

## Context

`FUNCTION_TREE.md` is the single status registry. A node should remain `[部分实现]` when its own capability lacks tests, contracts, evidence, or an explicit boundary. A-08 now covers its own capability: registry lifecycle material and validation.

The key distinction is:

- implemented: the lifecycle registry validator and evidence checks exist and are tested
- not claimed: the validator does not prove that every cited project feature is available at runtime

## Approach

Only update the registry status and evidence text for A-08. No runtime code changes are needed because the previous JSON-report package completed the missing machine-readable validator surface.

## Boundaries

- This change does not mark any downstream feature as implemented.
- This change does not broaden validator semantics.
- The validator remains conservative and non-executing.
