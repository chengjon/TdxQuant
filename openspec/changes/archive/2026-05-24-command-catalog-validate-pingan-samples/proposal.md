# Change: Command Catalog Validate PingAn Samples

## Why

`FUNCTION_TREE.md` records D-07 `PingAn buy / sell / confirm_current` as partially implemented with many fixed catalog follow-up bundles. Readers can discover those bundles by scanning runtime JSON, but the registry needs compact, non-executing evidence that the PingAn bundle surface is parseable and bounded in CLI output.

`catalog validate --view summary` already exposes task+report and submit-once bundle samples. Adding PingAn bundle count and bounded samples makes the D-07 catalog registration surface easier to verify while keeping validation strictly non-executing.

## What Changes

- Add PingAn bundle count and bounded sample fields to catalog validation payloads.
- Project those fields into `catalog validate --view summary`.
- Cover `catalog validate --kind bundle --label pingan --view summary` with CLI tests.
- Update `FUNCTION_TREE.md` D-07/E-11 evidence and boundary text after implementation.

## Non-Goals

- No new PingAn task/report/trade/bundle entries.
- No execution of catalog steps during validation.
- No expanded desktop automation or broker support.
- No arbitrary workflow builder.

