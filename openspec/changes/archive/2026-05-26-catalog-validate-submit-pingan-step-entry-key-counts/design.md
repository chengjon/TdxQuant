# Design: Catalog Validate Submit/PingAn Step Entry Key Counts

## Behavior

The summary view builder already copies `submit_once_bundle_step_entry_counts` and `pingan_bundle_step_entry_counts`. The new fields are computed as:

- `len(submit_once_bundle_step_entry_counts)`
- `len(pingan_bundle_step_entry_counts)`

The fields appear only in `catalog validate --view summary` output and remain derived from already parsed, non-executing catalog validation data.

## Boundary

The fields count distinct step-entry keys for selected subsets, not resolved steps. They do not expose complete manifests, prove entry availability, execute steps, or validate workflow semantics.

## Verification

- Add API CLI summary assertions comparing each key-count field to `len(<step_entry_counts>)`.
- Run API CLI tests, OpenSpec validation, diff check, and the FUNCTION_TREE validator.
