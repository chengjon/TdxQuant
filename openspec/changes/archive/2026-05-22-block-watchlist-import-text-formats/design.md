## Design

The existing JSON import schema remains the canonical rich format. CSV and TXT inputs are lightweight adapters that produce the same `WatchlistImportRequest` dataclass and then reuse the current planning and sync functions.

### CSV Format

CSV imports require a header row with `symbol` and `block_code`. Optional columns are `block_name`, `mode`, `create_if_missing`, and `mutation_key`. Blank symbol rows are ignored. If multiple non-empty `block_code` values appear they must all match after trimming.

### TXT Format

TXT imports use directive comments for import metadata and plain non-empty symbol lines for members. Supported directives are `# block_code=...`, `# block_name=...`, `# mode=merge|replace`, `# create_if_missing=true|false`, `# mutation_key=...`, and `# source=...`.

### Boundary

Text formats do not add any new write behavior. They only replace the file parsing step. The task command and sync execution still use the existing dry-run default and existing provider safety boundary.
