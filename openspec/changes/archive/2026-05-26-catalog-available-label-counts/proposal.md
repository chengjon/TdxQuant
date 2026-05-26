# Add catalog available label counts

## Why

Catalog list summary views already expose `available_entry_labels` and `available_bundle_labels` so callers can discover label filters without reading the full catalog payload. They do not expose the size of those discovery sets as an explicit machine-readable field.

E-11 remains a partial command-catalog registry node. Adding label counts keeps discovery summary views compact and easier to consume without turning catalog list/validate into execution or a workflow builder.

## What Changes

- Add read-only `available_entry_label_count` to catalog list summary views when `available_entry_labels` is projected.
- Add read-only `available_bundle_label_count` to catalog list summary views when `available_bundle_labels` is projected.
- Keep existing label arrays and matched entry/bundle counts unchanged.
- Do not execute catalog entries, bundle steps, task/report commands, submit-once flows, broker probes, or trade operations.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Touches `tdxquant/cli.py` catalog summary projection only.
- Adds focused CLI summary assertions.
- Updates `FUNCTION_TREE.md` E-11 with explicit evidence and boundary.
