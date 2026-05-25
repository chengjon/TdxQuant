## Design

`_validate_catalog_registry()` already iterates through selected resolved bundle steps and computes additive source/name/entry counts. During that same loop, when a step has string `source` and `name`, it will increment a deterministic `source:name` key.

The summary view will deep-copy this new map beside the existing bundle step count maps.

The field is strictly aggregate evidence:

- sum of values equals `bundle_step_count` for selected resolved bundle steps with source/name
- keys are compact `source:name` strings
- no step payloads are exposed
- no bundle execution behavior changes

## Risks

- The field duplicates information derivable from step details in code, but those details are intentionally not exposed in validation summary views. This map keeps E-11 evidence compact and bounded.
