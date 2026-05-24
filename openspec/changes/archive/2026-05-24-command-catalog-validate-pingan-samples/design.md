# Design: Command Catalog Validate PingAn Samples

## Approach

Extend the existing catalog validation bundle pass with a PingAn-oriented counter and sample list. A bundle is PingAn-oriented when the resolved bundle name, labels, or step entries contain `pingan`.

The validation payload will include:

- `pingan_bundle_count`
- `pingan_bundle_samples`
- `pingan_bundle_sample_limit`
- `pingan_bundle_sample_truncated`

The summary view copies these fields directly from the validation payload. Detailed validation remains the default printed result, and summary mode remains opt-in.

## Boundary

The new fields prove only that fixed PingAn bundle definitions can be resolved and sampled by catalog validation. They do not execute task/report/trade/bundle steps, do not prove real broker automation works, and do not add coverage for unimplemented dialogs, securities, brokers, or result branches.

## Validation

- Focused CLI tests for `catalog validate --kind bundle --label pingan --view summary`.
- Existing catalog CLI test module.
- OpenSpec strict validation.
- `FUNCTION_TREE.md` registry validation.
- Whitespace checks before and after archive.

