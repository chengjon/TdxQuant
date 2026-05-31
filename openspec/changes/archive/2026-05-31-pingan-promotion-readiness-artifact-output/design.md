# Design: PingAn promotion readiness rollup artifact output

## Overview

The task receives existing evidence paths, builds the read-only `promotion_readiness_rollup`, and may optionally persist the output to a caller-provided JSON path.

## Output Shape

The written JSON artifact will contain:

- `promotion_readiness_rollup`
- `task`
- `task_profile`
- `timing`

The task result will also include `promotion_readiness_rollup_artifact` with:

- `json_output_path`
- `written`
- `schema`

## Boundary

This artifact is an immutable review aid for the current command invocation. It does not refresh source evidence, does not execute any workflow, and does not imply production readiness. Operators remain responsible for choosing where artifacts live and for applying freshness thresholds when needed.

## Error Handling

If the output directory does not exist, the task creates it. If the file cannot be written, the task returns `INVALID_REQUEST` and preserves the read-only boundary by not attempting fallback workflow execution.

