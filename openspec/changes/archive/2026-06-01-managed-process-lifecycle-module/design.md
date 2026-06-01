## Context

The architecture review identified lifecycle governance as the clearest real seam in the codebase. Provider replay, subscription watch background control, and PingAn trade lifecycle each carry local implementations of process liveness, ownership, statefile, lock, supervisor, restart, and backoff behavior.

The first implementation slice should not rewrite all three domains at once. Provider replay and subscription watch background control are lower risk than PingAn desktop trading because they do not submit broker orders or drive UI automation. They are also already heavily tested through local state and fake process probes.

## Goals / Non-Goals

**Goals:**

- Create one shared module for managed-process lifecycle primitives.
- Make provider replay ownership diagnostics use the shared process liveness and provenance helpers.
- Make subscription watch background ownership diagnostics use the shared PID parsing/liveness and provenance helpers.
- Add tests proving adapter outputs carry shared lifecycle provenance.
- Preserve existing public behavior while adding additive diagnostic metadata.

**Non-Goals:**

- Do not change CLI command names, arguments, or execution behavior.
- Do not refactor PingAn trade lifecycle in this slice.
- Do not introduce new daemon supervisors or background processes.
- Do not change lock file formats, active statefile formats, or restart/backoff semantics.
- Do not promote or demote any `FUNCTION_TREE.md` node status.

## Decisions

1. Add a module, not a class hierarchy.

   The seam is currently a set of local lifecycle primitives, not an object model. A small function module gives callers leverage without forcing provider replay and subscription watch into a shared inheritance shape.

   Alternative considered: create a `ManagedProcessController` class. Rejected for this slice because the adapters already have domain-specific controllers and state paths; adding a generic controller would require more migration than needed to prove the seam.

2. Use additive provenance metadata for adapter proof.

   The adapter outputs should include a small `managed_lifecycle` object with schema, module, adapter name, and primitive names. This gives tests and reviewers explicit evidence that the shared module is used while keeping existing fields intact.

   Alternative considered: keep the refactor completely internal. Rejected because it would make this architecture slice harder to verify through stable outputs.

3. Start with provider replay and subscription watch background.

   These two lines already expose lifecycle read models and can be verified locally. PingAn trade lifecycle remains a later adapter because it is coupled to higher-risk desktop trading evidence and D-07/D-08 behavior.

   Alternative considered: migrate all three lifecycle lines in one change. Rejected because it would expand blast radius across real trade lifecycle control.

4. Keep domain-specific payload construction in the adapters.

   The shared module should own primitives such as PID coercion, liveness, ownership diagnostics, provenance, and backoff projection. It should not own provider replay config hashes, subscription watch run IDs, or broker-specific owner lock fields.

## Risks / Trade-offs

- Risk: additive provenance fields could be mistaken for a new runtime guarantee.
  Mitigation: specs and `FUNCTION_TREE.md` boundary text state that provenance is diagnostic evidence only and does not start, stop, restart, or supervise processes.

- Risk: shared primitives diverge from existing edge-case behavior.
  Mitigation: start with small primitives that preserve current semantics, and run focused provider replay and subscription watch tests.

- Risk: a partial migration leaves duplicate helpers in place.
  Mitigation: this is intentional for the first slice. The shared module is introduced where verifiable, then later slices can migrate lock/backoff/supervisor logic with smaller risk.

## Migration Plan

1. Add red tests for shared primitive outputs and adapter provenance.
2. Implement `tdxquant.managed_lifecycle`.
3. Wire provider replay liveness/ownership diagnostics through the shared module.
4. Wire subscription watch PID parsing/liveness and ownership projection through the shared module.
5. Update `FUNCTION_TREE.md` evidence and specs.
6. Archive and commit after focused and registry verification.

Rollback is straightforward: remove the additive provenance fields and restore local helper functions because public command syntax and persisted file formats are unchanged.
