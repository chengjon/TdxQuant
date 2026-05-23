# Design: OpenSpec Evidence Validation

## Context

The feature registry may cite many OpenSpec changes in a single evidence cell,
for example `OpenSpec `change-a` / `change-b``. Those ids should resolve to
checked-in OpenSpec material, but the validator currently only checks that the
evidence cell is non-empty.

## Decisions

### Evidence Reference Parsing

Parse backtick-delimited ids that appear after an `OpenSpec` marker in each
feature row evidence cell. This intentionally avoids interpreting unrelated
backtick snippets such as filenames or CLI flags as change ids.

### Resolution Rules

A referenced id is valid if either path exists:

- `openspec/changes/<id>/.openspec.yaml`
- `openspec/changes/archive/<date>-<id>/`

This supports active changes during work and archived changes after completion.

### Failure Output

Missing references fail validation with the feature row id, line number, and
missing OpenSpec change id.

## Risks

- Evidence text can be free-form. Mitigation: only validate ids explicitly
  attached to an `OpenSpec` marker and leave non-OpenSpec evidence untouched.
