# Design

## Context

Catalog planning resolves task/trade/report presets into command namespaces and summary views already include reduced `dispatch`, `resolved_args`, selected steps, provenance, and constraints. D-07/D-08 need a clearer boundary for trade-oriented catalog plans so a reader can tell that the plan is registered and input-resolved without mistaking it for an executable/live trade guarantee.

## Goals

- Make trade-related plan/preview summaries explicitly non-executing.
- Show the resolved trade command and relevant input field coverage.
- Support entry plans and selected bundle step summaries.
- Cover buy, sell, submit-once, guarded buy, and confirm-current workflows.

## Non-Goals

- Do not execute trade, task, report, or bundle dispatch.
- Do not add new PingAn desktop execution primitives.
- Do not infer live broker readiness or order safety from catalog metadata.
- Do not change `catalog run` execution semantics.

## Decisions

### 1. Derive the boundary from resolved dispatch and args

Catalog plan already produces `dispatch.command_name` and resolved args. The boundary is derived from those existing values, avoiding another source of truth.

### 2. Treat order-like and confirmation commands differently

Order-like commands (`trade-buy`, `trade-sell`, `trade-submit-once`, `guarded-trade-buy`) report required order input fields. `trade-confirm-current` reports the same non-execution boundary with an empty required input list because it confirms a current dialog rather than placing a new order.

### 3. Attach the boundary near the relevant plan object

Entry summaries get a top-level `trade_plan_boundary`. Bundle summaries keep boundaries on each trade-related selected step so report-only steps are not mislabeled.

## Risks / Trade-offs

- The boundary could be mistaken for a safety approval. It explicitly includes non-execution fields and does not replace trade safety checks.
- Required-field coverage is based on resolved catalog arguments, not live broker state. It only proves catalog planning resolved inputs.

