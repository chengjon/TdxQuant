## Context

Block sync currently accepts `mode=replace|merge`, `dry_run`, and `mutation_key`. This works, but higher-level callers need a clearer write-intent vocabulary and more explicit replay/conflict metadata in audit artifacts.

## Goals / Non-Goals

**Goals:**

- Add a small explicit policy enum for block sync write intent.
- Preserve existing `mode` and `dry_run` compatibility.
- Attach policy metadata to sync request, result, and audit artifacts.
- Make mutation-key replay and conflict outcomes machine-readable.

**Non-Goals:**

- No new block snapshot read path.
- No task/catalog/CLI wrappers in this slice.
- No new provider schema family.
- No change to live TDX block mutation execution semantics.

## Decisions

1. Keep existing `mode` and `dry_run` parameters as the compatibility surface.
   - Add optional `write_policy` rather than forcing every caller to migrate.
   - Policy can derive mode/dry-run, and explicit conflicting mode/dry-run combinations should fail deterministically.

2. Use a small enum:
   - `replace`: execute replace sync.
   - `merge`: execute merge sync.
   - `replace_dry_run`: plan replace sync only.
   - `merge_dry_run`: plan merge sync only.

3. Record policy metadata in the canonical request and audit payload.
   - This makes mutation-key replay compare policy as part of request identity.
   - Conflict feedback should include prior/current canonical requests.

## Risks / Trade-offs

- Adding policy while keeping mode/dry-run can create conflicting inputs. The implementation should reject conflicts rather than silently choosing one.
- Policy metadata changes canonical request identity, so old audit files without policy are tolerated but new conflict/replay decisions use the updated shape.

## Migration

Existing callers can keep using `mode` and `dry_run`; the system derives the equivalent policy. New callers can pass `write_policy` explicitly.

## Open Questions

- Whether future task/catalog wrappers should expose policy names directly.
