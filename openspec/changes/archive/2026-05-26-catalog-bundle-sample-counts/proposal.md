# Add catalog bundle sample counts

## Why

Catalog validate/plan summary views already expose bounded bundle samples for task+report, submit-once, and PingAn bundle subsets, along with sample limits and truncation flags. Automation can infer visible sample sizes by parsing arrays, but the registry has been moving toward explicit bounded counts for summary projections.

E-11 remains a partial command-catalog registry node. Adding explicit sample counts makes the summary easier to consume without turning catalog validation into execution or a workflow builder.

## What Changes

- Add read-only `task_report_bundle_sample_count` to catalog summary output when task+report bundle samples are present.
- Add read-only `submit_once_bundle_sample_count` to catalog summary output when submit-once bundle samples are present.
- Add read-only `pingan_bundle_sample_count` to catalog summary output when PingAn bundle samples are present.
- Keep sample limits/truncation flags and all existing bundle counts unchanged.
- Do not execute catalog entries, bundle steps, task/report commands, submit-once steps, or broker/PingAn flows.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Touches `tdxquant/cli.py` catalog summary projection only.
- Adds focused CLI summary tests.
- Updates `FUNCTION_TREE.md` E-11 as the single feature registry with explicit status, evidence, and boundary.
