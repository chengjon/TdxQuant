# Change: Command Catalog Validate Submit-Once Samples

## Why

`FUNCTION_TREE.md` currently records D-08 `PingAn submit_once` as partially implemented: the submit-once task/catalog/bundle entries exist, but readers need a compact, non-executing way to verify the registered submit-once bundle surface without reading the full runtime JSON files.

`catalog validate --view summary` already exposes task+report bundle counts and bounded samples. Extending that summary with submit-once bundle counts and bounded samples gives the single feature registry a concrete evidence point while preserving the existing boundary: validation parses catalog structure only and does not run task, report, trade, or bundle steps.

## What Changes

- Add submit-once bundle count and bounded sample fields to catalog validation payloads.
- Project those fields into `catalog validate --view summary`.
- Cover the fields with CLI tests that assert non-execution and deterministic bounded samples.
- Update `FUNCTION_TREE.md` D-08/E-11 evidence and boundary text after implementation.

## Non-Goals

- No new task/report/trade/bundle entries.
- No execution of catalog steps during validation.
- No new Ping An desktop execution primitive.
- No arbitrary workflow builder.

