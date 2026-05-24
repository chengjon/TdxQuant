## Overview

Add three additive scalar counts to `trade_plan_boundary` for trade-related catalog plan and preview summary views:

- `required_input_count`
- `provided_input_count`
- `missing_input_count`

The counts are derived from the existing required/provided/missing field arrays that are already present in `trade_plan_boundary`.

## Behavior

For trade entries and selected trade-related bundle steps:

- `required_input_count == len(required_input_fields)`
- `provided_input_count == len(provided_input_fields)`
- `missing_input_count == len(missing_input_fields)`

The output remains deterministic and non-executing. Existing field arrays remain the detailed source of truth.

## Boundary

The counts are a compact catalog plan summary only. They do not dispatch catalog entries, do not check broker readiness, do not approve safety constraints, and do not prove live trading availability.
