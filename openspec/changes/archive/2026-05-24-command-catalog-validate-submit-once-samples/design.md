# Design: Command Catalog Validate Submit-Once Samples

## Approach

Reuse the existing catalog validation pass that resolves matching bundles. While each bundle is resolved, derive whether it is submit-once-oriented from the resolved bundle name, labels, and step entries. For matching bundles:

- increment `submit_once_bundle_count`;
- append deterministic bundle names up to `SUBMIT_ONCE_BUNDLE_SAMPLE_LIMIT`;
- expose a truncation flag when more matches exist than samples.

The summary view copies the compact fields from the validation payload. Detailed validation remains the default payload, and summary mode remains opt-in.

## Boundary

The new fields are registry evidence only. They prove that matching bundle definitions can be parsed and sampled by catalog validation; they do not prove that a bundle can execute successfully, do not start task/report/trade commands, and do not add a separate sell submit-once desktop primitive.

## Validation

- Focused CLI tests for `catalog validate --kind bundle --label submit-once --view summary`.
- OpenSpec strict validation.
- `FUNCTION_TREE.md` registry validation.
- Whitespace check before and after archive.

