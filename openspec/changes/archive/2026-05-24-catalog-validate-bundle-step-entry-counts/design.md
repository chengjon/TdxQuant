# Design: Catalog Validate Bundle Step Entry Counts

## Overview

`_validate_catalog_registry()` already iterates through selected resolved bundle steps to compute source/name counts. The same pass will count each non-empty step `entry` into `bundle_step_entry_counts`.

## Data Shape

`bundle_step_entry_counts` is a sorted object:

- Key: resolved bundle step `entry`.
- Value: number of selected resolved bundle steps referencing that entry.

For the current runtime registry, every resolved bundle step has an entry, so the sum of values equals `bundle_step_count`.

## Projection

`_build_catalog_summary_view()` will deep-copy `bundle_step_entry_counts` into summary view payloads for `catalog validate --view summary`.

## Compatibility

This is additive. Existing validation fields and runtime catalog files do not change.
