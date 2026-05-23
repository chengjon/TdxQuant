## Context

The formula namespace mixes two different maturity levels. `formula.screen` has a provider-facing contract, replay fixtures, and normalized result semantics. Other formula actions still delegate to legacy bridge methods and do not have stable replay/provider contracts. `FUNCTION_TREE.md` needs a single, evidence-backed registry that makes that distinction machine-checkable and user-visible.

## Goals / Non-Goals

**Goals:**
- Provide a small in-repo registry with one row per public formula capability.
- Expose registry data through `TdxApiManager.formula.capabilities()` and a read-only CLI command.
- Mark `formula.screen` as provider-contract stable and mark legacy formula actions as bridge-only, non-provider-stable.
- Keep evidence and boundary text close to the executable registry so `FUNCTION_TREE.md` can cite concrete code/tests.

**Non-Goals:**
- No new formula execution behavior.
- No new replay fixture for bridge-only formula actions.
- No claim that bridge-only formula actions are safe in replay/provider-contract mode.
- No changes to raw TongDaXin formula output normalization outside `formula.screen`.

## Decisions

1. Add a dedicated registry module instead of embedding static data inside CLI code.
   - Rationale: manager, CLI, tests, and `FUNCTION_TREE.md` can point to one source.
   - Alternative considered: documenting the boundary only in `FUNCTION_TREE.md`. That leaves no executable surface for tests or callers.

2. Return plain dictionaries from the registry API.
   - Rationale: existing result payloads are JSON-first; dictionaries avoid leaking dataclass objects into CLI serialization.
   - Alternative considered: expose dataclasses directly. This would require extra serialization handling for little benefit.

3. Keep bridge-only formula capabilities visible in the registry.
   - Rationale: hiding unsupported provider contracts would make absence ambiguous. Explicit bridge-only rows prevent callers from treating unknown capabilities as stable.
   - Alternative considered: list only stable provider capabilities. This would not explain the boundary for existing formula methods.

## Risks / Trade-offs

- [Risk] The registry can drift from actual formula methods. -> Mitigate with tests asserting representative stable and bridge-only rows.
- [Risk] Users may still interpret listed bridge-only entries as provider-stable. -> Mitigate with explicit status, `provider_contract_stable=false`, and boundary text in every row.
- [Risk] A future formula provider contract may need richer metadata. -> Keep entries dictionary-shaped and additive so future fields can be added without breaking existing callers.
