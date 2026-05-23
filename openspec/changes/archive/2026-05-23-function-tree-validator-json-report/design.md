# Design

## Context

The validator currently returns:

- exit code `0` and a compact text summary on success
- exit code `1` and one error per stderr line on failure

That behavior must remain unchanged for existing shell users.

## Approach

Add an opt-in `--json` flag. The flag changes the selected output payload, not the validation semantics.

The JSON report shape:

- `valid`: boolean
- `row_count`: integer
- `status_counts`: object keyed by the existing status labels without backticks
- `problem_count`: integer
- `errors`: array of error strings

On success, JSON is printed to stdout and stderr stays empty. On failure, JSON is still printed to stdout and the process returns `1`; stderr remains empty for JSON mode so machine consumers have one payload channel.

## Boundaries

- Default text output is unchanged.
- Exit code semantics are unchanged.
- The validator still performs conservative structural checks only.
- The report does not execute evidence paths, interpret globbed evidence, or assert feature runtime availability.
