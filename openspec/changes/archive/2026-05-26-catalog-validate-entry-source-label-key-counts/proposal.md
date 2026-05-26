## Why

Catalog validate summary view already projects `entry_source_counts` and `entry_label_counts`, but callers need to count the distinct projected source and label keys themselves. Adding explicit key-count fields keeps the non-executing summary registry consistent with the other catalog count-map projections.

## What Changes

- Add `entry_source_key_count` to catalog validate summary view, derived from the number of keys in `entry_source_counts`.
- Add `entry_label_key_count` to catalog validate summary view, derived from the number of keys in `entry_label_counts`.
- Keep the fields read-only and non-executing; they do not expose full entry manifests, execute catalog entries, or change entry filtering/label semantics.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: Catalog validate summary view exposes entry source/label key-count fields derived from already projected count maps.

## Impact

- `tdxquant/cli.py`: summary view projection adds two derived count fields.
- `tests/test_api_cli.py`: catalog validate summary tests assert the new fields and non-execution behavior.
- `FUNCTION_TREE.md`: E-11 evidence/boundary registry is updated without promoting the node to fully implemented.
