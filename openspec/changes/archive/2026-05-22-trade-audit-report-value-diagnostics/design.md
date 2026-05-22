## Context

Trade audit daily and period reports already load local audit JSON files, filter by time/status/method/broker/submission key, and expose count-oriented summaries such as `by_code`, `by_status`, and `by_day`. Audit result payloads may contain order input fields like `price` and `quantity`, but the reports currently do not summarize those fields.

## Goals / Non-Goals

**Goals:**

- Add a deterministic requested-value diagnostic to daily and period reports.
- Make coverage explicit by counting priced and unpriced entries.
- Group requested value by status and method for triage.
- Preserve existing report output fields and filters.

**Non-Goals:**

- Do not claim filled value, average fill price, slippage, fees, execution quality, or PnL.
- Do not query broker accounts, positions, orders, or trades.
- Do not mutate audit files or ledgers.
- Do not change report preset names or CLI arguments.

## Decisions

- Read `price` and `quantity` from each audit entry's existing `result.data` payload.
- Treat an entry as priced only when both fields are present and numeric.
- Serialize requested value as a decimal string to avoid binary floating-point artifacts in JSON.
- Include `calculation` text in `value_diagnostics` so consumers do not mistake requested value for fills or PnL.
- Attach the same diagnostic shape to both daily and period report payloads.

## Risks / Trade-offs

- Some historical audit payloads do not contain `price` or `quantity`; the diagnostic therefore includes explicit `unpriced_entries`.
- Requested order value is not the same as executed value. The boundary must remain visible in `FUNCTION_TREE.md` and in the diagnostic payload.
