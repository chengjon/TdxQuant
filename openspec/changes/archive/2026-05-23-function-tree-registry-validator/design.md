# Design: FUNCTION_TREE Registry Validator

## Context

`FUNCTION_TREE.md` uses a Markdown table where each feature row starts with an id
like `A-01`. The important registry contract is structural: a reader must be
able to distinguish implemented, partial, designed/pending, and boundary-only
nodes, with evidence and boundary text present on every row.

## Decisions

### Shape Validation

The validator parses only feature rows matching `| <letter>-<number> | ... |`.
It validates:

- unique node ids
- one of the allowed status tokens:
  - `` `[已实现]` ``
  - `` `[部分实现]` ``
  - `` `[已设计/待实现]` ``
  - `` `[非目标/边界]` ``
- non-empty evidence and boundary columns
- designed/pending rows must include boundary language that makes pending or
  unavailable status explicit
- root `ROADMAP.md` must not exist

### Command Output

The script prints a compact summary on success and actionable line-level errors
on failure. It exits non-zero if validation fails.

### Scope Boundary

The validator checks registry structure only. It does not inspect source code,
run tests, or decide whether an evidence path proves runtime availability.

## Risks

- Markdown tables with escaped pipes may be parsed imperfectly. Mitigation:
  keep parsing intentionally scoped to the current registry row format and cover
  expected failure modes with tests.
