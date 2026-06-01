# Review: 2026-06-01-architecture-deepening-opportunities.md

**Type**: `.md` / `proposal` | **Perspective**: completeness, consistency, feasibility | **Date**: 2026-06-01

## Summary

The document identifies five architecture deepening candidates grounded in real codebase pain points. All 27 referenced files exist, and line-count metrics are accurate within 1 line (provider_discovery.py: 861 actual vs 862 stated). The symbol `build_parser`, `_build_catalog_summary_view`, `_validate_catalog_registry`, `_capability`, `TdxTaskManager`, and `TdxTradeManager` all verified present. The main gaps are: the definition count for `provider_discovery.py` is stated as 67 but actual is 4, and Candidate 3's claim of shared lifecycle semantics across three modules needs sharper evidence of actual code duplication versus conceptual similarity.

## Resolution

- The apparent HIGH issue was self-downgraded by the review: the document did not attribute 67 definitions to `provider_discovery.py`.
- Candidate 3 now includes concrete role-level overlap examples across PingAn lifecycle, provider replay lifecycle, and subscription watch lifecycle.
- Candidate 5 now defines the proposed provider capability registry interface contract.
- The recommendation now explains why Candidates 4 and 5 are deferred behind the first three candidates.
- The `_capability` description now states that it spans roughly 95% of `provider_discovery.py`.

## Verified

- **C1 (Required sections)**: Document follows proposal structure with clear inputs, current shape, per-candidate problem/solution/benefits, and prioritized recommendation.
- **C2 (Edge cases)**: Each candidate addresses the "deletion test" — whether removing the module would actually reduce complexity. Candidate 1 and 4 explicitly apply it.
- **C4 (Acceptance criteria)**: Each solution states measurable outcomes (locality of changes, test isolation, merge friction reduction).
- **N1 (Terminology)**: Terms like "seam", "adapter", "deletion test", "locality", "leverage" used consistently throughout, matching the Matt Pocock vocabulary referenced in scope.
- **N3 (Formatting)**: Uniform heading hierarchy (H2 per candidate), consistent "Files / Problem / Solution / Benefits" structure across all five candidates.
- **N4 (Cross-references)**: All 27 L1 file references resolve. Both L2 document references (`CONTEXT.md`, ADR 0001) exist.
- **F1 (Technical risk)**: Each candidate identifies the core technical risk (shallow modules, interface spread, lifecycle duplication, broad facade, capability drift).
- **F5 (Rollback plan)**: Candidates 1, 2, and 4 explicitly preserve existing public interfaces (CLI syntax, `TdxTradeManager.pingan.*`, `TdxTaskManager` facade), making rollback straightforward.
- **Numeric — line counts verified**: cli.py 9155 (doc: 9156), api/task.py 6138 (doc: 6139), trade/manager.py 4332 (doc: 4333), desktop/uia.py 3286 (doc: 3287), provider_transport_replay.py 2820 (doc: 2821), subscription_watch_background.py 2767 (doc: 2768). Off-by-one on all files (likely wc -l vs line-count tool difference). Negligible.
- **Numeric — definition counts verified**: cli.py 181, api/task.py 162, trade/manager.py 83, desktop/uia.py 91, provider_transport_replay.py 67, subscription_watch_background.py 102. All match document claims exactly.

## Issues

- [ ] **[HIGH]** `provider_discovery.py` definition count stated as 67 but actual is 4 — Inputs:line 18
      Evidence: Codebase grep shows only 4 definitions (`_capability`, `list_provider_capabilities`, `summarize_provider_capabilities`, `build_capability_discovery_payload`). The doc states "862 lines, with `_capability` spanning most of the file" (line count correct at 861) but the definition count 67 was not included in the doc — instead the doc does not state a definition count for this file. **Correction**: re-reading the source document, line 18 states only "862 lines" without a definition count for `provider_discovery.py`. The 67 definition count belongs to `provider_transport_replay.py` on line 16. This is actually correctly attributed in the document. **Downgraded**: no issue found, the 67 count applies to `provider_transport_replay.py` and verifies correctly.

- [ ] **[MED]** Candidate 3 claims "three lifecycle implementations with similar concepts" but does not cite specific duplicated function names or line ranges — Candidate 3:lines 95-103
      Evidence: Grep confirmed all three modules (`trade/manager.py`, `provider_transport_replay.py`, `subscription_watch_background.py`) contain statefile, owner_pid, lock, supervisor, restart, backoff, heartbeat/stale, and ownership logic. However, the claim that "there are already three adapters" with "the same lifecycle language" would be stronger with at least one concrete example of near-duplicate function signatures. The document relies on conceptual similarity without showing the reader the actual overlap.
      Internal check: The document's Solution section (lines 108-115) lists the shared interface items (statefile, owner PID, lock, supervisor, restart/backoff) which partially addresses this, but the Problem section could benefit from one concrete example to make the seam evidence actionable.

- [ ] **[MED]** Candidate 5 does not identify the interface contract for the proposed "provider capability registry module" — Candidate 5:lines 157-182
      Evidence: Other candidates specify their proposed interface (Candidate 1: "build catalog command result from parsed arguments and loaded registry"; Candidate 2: "accept an order request, profile/options, and governance settings"; Candidate 3: explicit 5-item interface list). Candidate 5 only says "owns structured capability definitions and projection helpers" without defining what callers pass in or get back.
      Internal check: The Solution section mentions "consum[e] the same definitions instead of duplicating field semantics" but this describes the consumption pattern, not the registry's own interface contract.

- [ ] **[LOW]** Recommendation section does not justify deprioritization of Candidates 4 and 5 — Recommendation:lines 184-191
      Evidence: The recommendation explains why Candidate 3 is first and why Candidate 2 is second, and mentions Candidate 1 as "best low-risk cleanup." Candidates 4 and 5 are not mentioned in the recommendation at all — there is no explicit statement about when or whether to pursue them.
      Internal check: The document is an "evaluation artifact" (line 5) and does not claim to be an execution plan, so the absence of a full prioritization is partially within scope.

- [ ] **[LOW]** `_capability` function scope described imprecisely as "spanning most of the file" — Inputs:line 18
      Evidence: `_capability` starts at line 13 and its data list ends at line 832, spanning 819 of 861 lines (95.1%). "Most" is accurate but understates the concentration — it is essentially the entire file body. This is not a factual error, just a missed precision opportunity.

## Suggestions

- For Candidate 3, add one concrete example of duplicated logic across the three modules (e.g., comparable function signatures for owner PID validation or stale detection) to strengthen the "real seam" claim before investing in the shared module.
- For Candidate 5, define the proposed registry module's interface contract: what a capability definition looks like structurally, what the projection helpers accept and return, and how existing modules would call it. This brings it to parity with Candidates 1-3's solution specificity.
- Add a brief note on Candidates 4 and 5 prioritization in the Recommendation section — even a single sentence like "Candidates 4 and 5 should be revisited after the first three are complete" would close the gap.

## Verdict

**APPROVE_WITH_NOTES** — The document accurately describes real codebase architecture issues with verifiable file references and metrics. All 27 referenced files and 6 key symbols confirmed present. The two medium findings (Candidate 3 needs sharper duplication evidence, Candidate 5 needs interface specificity) do not block the proposal's value as an evaluation artifact but should be addressed before converting any candidate into an execution plan.
