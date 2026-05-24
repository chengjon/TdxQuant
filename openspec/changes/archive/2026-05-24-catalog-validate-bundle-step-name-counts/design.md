# Design: Catalog Validate Bundle Step Name Counts

## Overview

During bundle validation, `_validate_catalog_registry()` already iterates through resolved selected bundle steps to compute aggregate counts. The same pass will count each non-empty step `name` into `bundle_step_name_counts`.

## Data Shape

`bundle_step_name_counts` is a sorted object:

- Key: resolved bundle step `name`.
- Value: number of selected resolved bundle steps with that name.

The sum of values equals `bundle_step_count` when every selected resolved bundle step has a non-empty `name`, which is true for the current runtime bundle registry.

## Projection

`_build_catalog_summary_view()` will deep-copy `bundle_step_name_counts` into summary view payloads for `catalog validate --view summary`.

## Compatibility

This is additive. Existing validation fields and runtime catalog files do not change.
