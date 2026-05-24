## Design

The detailed governance object is the source of truth for advisory reasons and actions. `action_count` is computed from the existing `actions` list immediately after actions are built, beside the existing `reason_count` field.

CLI and HTTP summary views continue to omit full `actions`. When the detailed governance payload contains an `actions` list, each summary view derives `action_count` from that list and keeps the existing bounded `action_samples`, `action_sample_limit`, and `action_sample_truncated` fields.

This keeps the field additive and deterministic:

- detailed payload: `action_count == len(governance.actions)`
- summary payload: `action_count == len(detailed governance.actions)`
- no lifecycle side effects

## Risks

- The field duplicates information already available as `action_summary.count`; tests will assert consistency so clients can use either representation without ambiguity.
