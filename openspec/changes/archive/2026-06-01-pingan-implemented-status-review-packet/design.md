## Context

The promotion readiness rollup already aggregates preflight, dialog readiness, acceptance coverage, freshness, evidence contract, artifact provenance, and live/manual acceptance provenance gates. When all gates pass, the decision becomes `eligible_for_review`, but the output does not yet provide a standalone packet a maintainer can use for explicit status review.

## Goals / Non-Goals

**Goals:**

- Emit `implemented_status_review_packet` from the existing rollup calculation.
- Preserve the fail-closed decision while adding review-oriented fields: target nodes, expected current status, review status, satisfied gates, blocked reasons, evidence summaries, and manual confirmation items.
- Make it explicit that no automatic FUNCTION_TREE transition happened.

**Non-Goals:**

- Do not promote D-07/D-08 to `[已实现]`.
- Do not add an automatic status transition writer.
- Do not execute PingAn broker, desktop, trade, report, catalog, task, or bundle workflows.
- Do not generate or refresh source readiness evidence.

## Decisions

- Build the packet inside `_build_pingan_promotion_readiness_rollup` after the decision is computed. This keeps it derived from the same evidence snapshot as the decision.
- Use schema `tdx.desktop_trade.pingan_implemented_status_review_packet.v1`.
- Always include a packet, even when blocked. A blocked packet explains why review cannot proceed; an eligible packet tells the maintainer which manual confirmations remain before any separate status change.
- Keep persistence unchanged. Existing `--json-output-path` already writes the full rollup artifact, so the packet is persisted when the rollup artifact is persisted.

## Risks / Trade-offs

- The packet can make evidence easier to review, but it still cannot prove production readiness by itself. The packet must carry `manual_status_review_required=true` and `function_tree_status_transition_executed=false`.
- The packet duplicates some rollup fields in a review-friendly shape. This is acceptable because the packet is a derived view, not a second source of truth.
