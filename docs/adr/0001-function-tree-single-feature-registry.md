# ADR 0001: FUNCTION_TREE Is the Single Feature Registry

## Status

Accepted

## Context

The project needs to describe both available capabilities and designed or future capabilities without misleading readers into thinking unavailable work is already usable.

A separate roadmap would create a competing source of truth and make it harder to know which feature state is authoritative.

## Decision

`FUNCTION_TREE.md` is the single feature registry and status source for TdxQuant.

Every feature node must explicitly state:

- Status: `[已实现]`, `[部分实现]`, `[已设计/待实现]`, or `[非目标/边界]`.
- Evidence: source, tests, runtime config, fixture, archived OpenSpec, or durable contract documentation.
- Boundary: the current guarantee and the claims the feature does not make.

Designed or future capabilities may be recorded in `FUNCTION_TREE.md`, but must use explicit status and boundary language. Do not create a competing `ROADMAP.md`.

## Consequences

- Architecture and planning work must update `FUNCTION_TREE.md` when feature status, evidence, or boundaries change.
- Historical docs can provide background, but `FUNCTION_TREE.md` wins when status conflicts.
- OpenSpec changes and archived specs are evidence inputs, not replacements for the feature registry.
