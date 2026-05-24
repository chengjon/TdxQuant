# Design: Subscription Governance Reason Summary

## Overview

The status builder will add `governance.reason_summary`, derived from the existing ordered `governance.reasons` list. The summary is additive and advisory-only.

## Data Shape

`governance.reason_summary` contains:

- `count`: number of advisory reasons.
- `primary_reason`: first advisory reason, or `null` when no reasons exist.
- `primary_source`: prefix before `:` in the first advisory reason, or `null` when no reasons exist.
- `source_counts`: sorted count map using the same source parsing as `reason_source_counts`.

## Projection

The CLI and HTTP summary views copy `reason_summary` when present. They continue to omit raw `governance.reasons` and raw `governance.actions`, and they keep existing bounded samples unchanged.

## Compatibility

The change is additive. Existing callers can ignore the new object. No existing field is removed or renamed.
